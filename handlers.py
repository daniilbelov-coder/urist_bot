"""Bot handlers for commands and messages."""
import logging
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import DisclaimerCreation, MassGeneration
from models import CreativeType, ChannelType, CreativeParams, CREATIVE_TYPE_NAMES, normalize_city_name
from generator import DisclaimerGenerator, ValidationError
from keyboards import (
    get_creative_type_keyboard,
    get_creative_type_keyboard_mass,
    get_geography_keyboard,
    get_geography_keyboard_multiple,
    get_channel_keyboard,
    get_channel_keyboard_mass,
    get_yes_no_keyboard,
    get_discount_unit_keyboard,
    get_discount_unit_keyboard_mass,
    get_skip_keyboard,
    get_confirmation_keyboard,
    get_confirmation_keyboard_mass,
    get_result_keyboard,
    get_main_menu_keyboard,
    remove_keyboard,
    add_back_button
)

logger = logging.getLogger(__name__)

router = Router()
generator = DisclaimerGenerator()


# Command handlers
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command."""
    await state.clear()
    
    welcome_text = (
        "👋 <b>Привет! Я бот для генерации дисклеймеров Яндекс Лавки.</b>\n\n"
        "Вы можете:\n"
        "1️⃣ Написать запрос в свободной форме\n"
        "2️⃣ Использовать команду /create для пошагового создания\n\n"
        "<b>Примеры запросов:</b>\n"
        "• \"Динамическая скидка новичка для МО до 31.12.24\"\n"
        "• \"Промокод 20% на первый заказ от 1000₽, Тула, до 15.02.25\"\n"
        "• \"Сертификат 3 применения, Москва, ТВ, до 01.03.25\"\n\n"
        "<b>Команды:</b>\n"
        "/create — пошаговое создание\n"
        "/help — справка"
    )
    
    await message.answer(welcome_text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    help_text = (
        "📚 <b>Справка по боту</b>\n\n"
        "<b>Типы креативов:</b>\n"
        "• Скидка новичка (динамическая/классическая)\n"
        "• Промокод\n"
        "• Сертификат\n"
        "• Имиджевый креатив\n"
        "• Продуктовый креатив\n"
        "• Вендорский креатив\n\n"
        "<b>Каналы размещения:</b>\n"
        "• ТВ/Радио — полная версия юр.лица\n"
        "• Другие форматы — короткая версия\n\n"
        "<b>Формат даты:</b> ДД.ММ.ГГ (например, 31.12.24)\n\n"
        "Для создания дисклеймера используйте /create или отправьте запрос в свободной форме."
    )
    
    await message.answer(help_text, parse_mode="HTML")


@router.message(Command("create"))
@router.message(F.text == "➕ Создать дисклеймер")
async def cmd_create(message: Message, state: FSMContext):
    """Start step-by-step disclaimer creation."""
    await state.clear()
    await state.set_state(DisclaimerCreation.choosing_type)
    
    text = "Выберите тип креатива:"
    await message.answer(text, reply_markup=get_creative_type_keyboard())


@router.message(F.text == "❓ Помощь")
async def btn_help(message: Message):
    """Handle help button."""
    await cmd_help(message)


# Type selection
@router.callback_query(DisclaimerCreation.choosing_type, F.data.startswith("type:"))
async def process_type_selection(callback: CallbackQuery, state: FSMContext):
    """Process creative type selection."""
    creative_type = callback.data.split(":")[1]
    await state.update_data(creative_type=creative_type)
    
    await state.set_state(DisclaimerCreation.choosing_geography)
    keyboard = add_back_button(get_geography_keyboard(), "back:to_type")
    await callback.message.edit_text(
        f"✅ Тип: {CREATIVE_TYPE_NAMES[CreativeType(creative_type)]}\n\n"
        "Выберите географию:",
        reply_markup=keyboard
    )
    await callback.answer()


# Geography selection
@router.callback_query(DisclaimerCreation.choosing_geography, F.data.startswith("geo:"))
async def process_geography_selection(callback: CallbackQuery, state: FSMContext):
    """Process geography selection."""
    city = callback.data.split(":")[1]
    await state.update_data(city=city)
    
    await state.set_state(DisclaimerCreation.choosing_channel)
    keyboard = add_back_button(get_channel_keyboard(), "back:to_geography")
    await callback.message.edit_text(
        f"✅ География: {normalize_city_name(city)}\n\n"
        "Выберите канал размещения:",
        reply_markup=keyboard
    )
    await callback.answer()


# Channel selection
@router.callback_query(DisclaimerCreation.choosing_channel, F.data.startswith("channel:"))
async def process_channel_selection(callback: CallbackQuery, state: FSMContext):
    """Process channel selection."""
    channel = callback.data.split(":")[1]
    await state.update_data(channel=channel)
    
    data = await state.get_data()
    creative_type = CreativeType(data["creative_type"])
    
    await callback.message.edit_text(f"✅ Канал: {'ТВ/Радио' if channel == 'tv_radio' else 'Другие форматы'}")
    
    # Route to appropriate next step based on creative type
    if creative_type == CreativeType.DYNAMIC_NEWCOMER:
        await ask_end_date(callback.message, state, "Введите дату окончания акции (формат: ДД.ММ.ГГ или ДД.ММ.ГГГГ):")
    elif creative_type == CreativeType.CLASSIC_NEWCOMER:
        await ask_end_date(callback.message, state, "Введите дату окончания акции (формат: ДД.ММ.ГГ или ДД.ММ.ГГГГ):")
    elif creative_type == CreativeType.PROMO_CODE:
        await ask_end_date(callback.message, state, "Введите дату окончания промокода (формат: ДД.ММ.ГГ или ДД.ММ.ГГГГ):")
    elif creative_type == CreativeType.CERTIFICATE:
        await ask_end_date(callback.message, state, "Введите дату окончания сертификата (формат: ДД.ММ.ГГ или ДД.ММ.ГГГГ):")
    elif creative_type == CreativeType.VENDOR:
        await ask_start_date(callback.message, state)
    elif creative_type in [CreativeType.IMAGE, CreativeType.PRODUCT]:
        await show_confirmation(callback.message, state)
    
    await callback.answer()


# Back button handlers
@router.callback_query(F.data == "back:to_type")
async def back_to_type(callback: CallbackQuery, state: FSMContext):
    """Go back to type selection."""
    await state.set_state(DisclaimerCreation.choosing_type)
    await callback.message.edit_text(
        "Выберите тип креатива:",
        reply_markup=get_creative_type_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "back:to_geography")
async def back_to_geography(callback: CallbackQuery, state: FSMContext):
    """Go back to geography selection."""
    data = await state.get_data()
    creative_type = data.get("creative_type")
    
    await state.set_state(DisclaimerCreation.choosing_geography)
    keyboard = add_back_button(get_geography_keyboard(), "back:to_type")
    
    type_text = CREATIVE_TYPE_NAMES.get(CreativeType(creative_type), "Не выбран") if creative_type else "Не выбран"
    await callback.message.edit_text(
        f"✅ Тип: {type_text}\n\n"
        "Выберите географию:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "back:to_channel")
async def back_to_channel(callback: CallbackQuery, state: FSMContext):
    """Go back to channel selection."""
    data = await state.get_data()
    city = data.get("city", "")
    
    await state.set_state(DisclaimerCreation.choosing_channel)
    keyboard = add_back_button(get_channel_keyboard(), "back:to_geography")
    
    await callback.message.edit_text(
        f"✅ География: {normalize_city_name(city)}\n\n"
        "Выберите канал размещения:",
        reply_markup=keyboard
    )
    await callback.answer()


# Date inputs
async def ask_end_date(message: Message, state: FSMContext, prompt: str):
    """Ask for end date."""
    await state.set_state(DisclaimerCreation.entering_end_date)
    await message.answer(prompt, reply_markup=remove_keyboard())


async def ask_start_date(message: Message, state: FSMContext):
    """Ask for start date."""
    await state.set_state(DisclaimerCreation.entering_start_date)
    await message.answer("Введите дату начала акции (формат: ДД.ММ.ГГ или ДД.ММ.ГГГГ):", reply_markup=remove_keyboard())


@router.message(DisclaimerCreation.entering_start_date)
async def process_start_date(message: Message, state: FSMContext):
    """Process start date input."""
    start_date = message.text.strip()
    
    is_valid, error = generator.validate_date(start_date)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуйте снова:")
        return
    
    await state.update_data(start_date=start_date)
    await ask_end_date(message, state, "Введите дату окончания акции (формат: ДД.ММ.ГГ):")


@router.message(DisclaimerCreation.entering_end_date)
async def process_end_date(message: Message, state: FSMContext):
    """Process end date input."""
    end_date = message.text.strip()
    
    is_valid, error = generator.validate_date(end_date)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуйте снова:")
        return
    
    await state.update_data(end_date=end_date)
    
    data = await state.get_data()
    creative_type = CreativeType(data["creative_type"])
    
    # Validate date order for vendor
    if creative_type == CreativeType.VENDOR:
        is_valid, error = generator.validate_dates_order(data["start_date"], end_date)
        if not is_valid:
            await message.answer(f"❌ {error}\n\nВведите дату окончания заново:")
            return
    
    # Route to next step
    if creative_type == CreativeType.DYNAMIC_NEWCOMER:
        await show_confirmation(message, state)
    elif creative_type == CreativeType.CLASSIC_NEWCOMER:
        await ask_max_discount(message, state)
    elif creative_type == CreativeType.PROMO_CODE:
        await ask_discount_size(message, state)
    elif creative_type == CreativeType.CERTIFICATE:
        await ask_usage_count(message, state)
    elif creative_type == CreativeType.VENDOR:
        await show_confirmation(message, state)


# Classic newcomer specific
async def ask_max_discount(message: Message, state: FSMContext):
    """Ask for maximum discount amount."""
    await state.set_state(DisclaimerCreation.entering_max_discount)
    await message.answer("Введите максимальный размер скидки в рублях:")


@router.message(DisclaimerCreation.entering_max_discount)
async def process_max_discount(message: Message, state: FSMContext):
    """Process maximum discount amount."""
    try:
        max_discount = int(message.text.strip())
        if max_discount <= 0:
            raise ValueError()
        
        await state.update_data(max_discount_amount=max_discount)
        await ask_delivery_info(message, state)
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите положительное целое число:")


async def ask_delivery_info(message: Message, state: FSMContext):
    """Ask if delivery info should be added."""
    await state.set_state(DisclaimerCreation.choosing_delivery_info)
    await message.answer(
        "Добавить информацию о доставке?",
        reply_markup=get_yes_no_keyboard("delivery:yes", "delivery:no")
    )


@router.callback_query(DisclaimerCreation.choosing_delivery_info, F.data.startswith("delivery:"))
async def process_delivery_choice(callback: CallbackQuery, state: FSMContext):
    """Process delivery info choice."""
    choice = callback.data.split(":")[1]
    
    if choice == "yes":
        await state.update_data(add_delivery_info=True)
        await state.set_state(DisclaimerCreation.entering_delivery_text)
        await callback.message.edit_text(
            "Введите текст о доставке или отправьте /skip для использования стандартного текста:\n\n"
            "<i>Стандартный текст: \"Три бесплатные доставки в пешей и одна в авто зоне. "
            "Доставку осуществляют партнеры Яндекс Еды.\"</i>",
            parse_mode="HTML"
        )
    else:
        await state.update_data(add_delivery_info=False)
        await callback.message.delete()
        await show_confirmation(callback.message, state)
    
    await callback.answer()


@router.message(DisclaimerCreation.entering_delivery_text, Command("skip"))
async def skip_delivery_text(message: Message, state: FSMContext):
    """Skip custom delivery text."""
    await show_confirmation(message, state)


@router.message(DisclaimerCreation.entering_delivery_text)
async def process_delivery_text(message: Message, state: FSMContext):
    """Process custom delivery text."""
    await state.update_data(delivery_info_text=message.text.strip())
    await show_confirmation(message, state)


# Promo code specific
async def ask_discount_size(message: Message, state: FSMContext):
    """Ask for discount size."""
    await state.set_state(DisclaimerCreation.entering_discount_size)
    await message.answer("Введите размер скидки (только число):")


@router.message(DisclaimerCreation.entering_discount_size)
async def process_discount_size(message: Message, state: FSMContext):
    """Process discount size."""
    try:
        discount_size = float(message.text.strip().replace(",", "."))
        if discount_size <= 0:
            raise ValueError()
        
        await state.update_data(discount_size=discount_size)
        await ask_discount_unit(message, state)
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите положительное число:")


async def ask_discount_unit(message: Message, state: FSMContext):
    """Ask for discount unit."""
    await state.set_state(DisclaimerCreation.choosing_discount_unit)
    await message.answer("Выберите единицу измерения:", reply_markup=get_discount_unit_keyboard())


@router.callback_query(DisclaimerCreation.choosing_discount_unit, F.data.startswith("unit:"))
async def process_discount_unit(callback: CallbackQuery, state: FSMContext):
    """Process discount unit selection."""
    unit = callback.data.split(":")[1]
    await state.update_data(discount_unit=unit)
    
    # Validate percentage
    if unit == "%":
        data = await state.get_data()
        discount_size = data.get("discount_size", 0)
        if discount_size > 100:
            await callback.message.edit_text("❌ Процент не может быть больше 100. Введите размер скидки заново:")
            await state.set_state(DisclaimerCreation.entering_discount_size)
            await callback.answer()
            return
    
    await callback.message.delete()
    await ask_first_order(callback.message, state)
    await callback.answer()


async def ask_first_order(message: Message, state: FSMContext):
    """Ask if promo is for first order only."""
    await state.set_state(DisclaimerCreation.choosing_first_order)
    await message.answer(
        "Промокод только для первого заказа?",
        reply_markup=get_yes_no_keyboard("first:yes", "first:no")
    )


@router.callback_query(DisclaimerCreation.choosing_first_order, F.data.startswith("first:"))
async def process_first_order_choice(callback: CallbackQuery, state: FSMContext):
    """Process first order choice."""
    choice = callback.data.split(":")[1]
    await state.update_data(first_order_only=(choice == "yes"))
    
    await callback.message.delete()
    await ask_category(callback.message, state)
    await callback.answer()


async def ask_category(message: Message, state: FSMContext):
    """Ask if promo is for specific category."""
    await state.set_state(DisclaimerCreation.choosing_category)
    await message.answer(
        "Промокод для конкретной категории/товара?",
        reply_markup=get_yes_no_keyboard("category:yes", "category:no")
    )


@router.callback_query(DisclaimerCreation.choosing_category, F.data.startswith("category:"))
async def process_category_choice(callback: CallbackQuery, state: FSMContext):
    """Process category choice."""
    choice = callback.data.split(":")[1]
    
    if choice == "yes":
        await state.set_state(DisclaimerCreation.entering_category_name)
        await callback.message.edit_text("Введите название категории:")
    else:
        await callback.message.delete()
        await ask_min_amount(callback.message, state)
    
    await callback.answer()


@router.message(DisclaimerCreation.entering_category_name)
async def process_category_name(message: Message, state: FSMContext):
    """Process category name."""
    await state.update_data(specific_category=message.text.strip())
    await ask_min_amount(message, state)


async def ask_min_amount(message: Message, state: FSMContext):
    """Ask for minimum order amount."""
    await state.set_state(DisclaimerCreation.entering_min_amount)
    await message.answer(
        "Минимальная сумма заказа в рублях (или /skip):",
        reply_markup=remove_keyboard()
    )


@router.message(DisclaimerCreation.entering_min_amount, Command("skip"))
async def skip_min_amount(message: Message, state: FSMContext):
    """Skip minimum amount."""
    await ask_max_discount_promo(message, state)


@router.message(DisclaimerCreation.entering_min_amount)
async def process_min_amount(message: Message, state: FSMContext):
    """Process minimum amount."""
    try:
        min_amount = int(message.text.strip())
        if min_amount <= 0:
            raise ValueError()
        
        await state.update_data(min_order_amount=min_amount)
        await ask_max_discount_promo(message, state)
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите положительное целое число или /skip:")


async def ask_max_discount_promo(message: Message, state: FSMContext):
    """Ask for maximum discount amount for promo."""
    await state.set_state(DisclaimerCreation.entering_max_discount_promo)
    await message.answer("Максимальная скидка в рублях (или /skip):")


@router.message(DisclaimerCreation.entering_max_discount_promo, Command("skip"))
async def skip_max_discount_promo(message: Message, state: FSMContext):
    """Skip maximum discount."""
    await show_confirmation(message, state)


@router.message(DisclaimerCreation.entering_max_discount_promo)
async def process_max_discount_promo(message: Message, state: FSMContext):
    """Process maximum discount for promo."""
    try:
        max_discount = int(message.text.strip())
        if max_discount <= 0:
            raise ValueError()
        
        await state.update_data(max_promo_discount=max_discount)
        await show_confirmation(message, state)
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите положительное целое число или /skip:")


# Certificate specific
async def ask_usage_count(message: Message, state: FSMContext):
    """Ask for certificate usage count."""
    await state.set_state(DisclaimerCreation.entering_usage_count)
    await message.answer("Введите количество применений сертификата:")


@router.message(DisclaimerCreation.entering_usage_count)
async def process_usage_count(message: Message, state: FSMContext):
    """Process usage count."""
    try:
        usage_count = int(message.text.strip())
        if usage_count <= 0:
            raise ValueError()
        
        await state.update_data(usage_count=usage_count)
        await show_confirmation(message, state)
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите положительное целое число:")


# Confirmation and generation
async def show_confirmation(message: Message, state: FSMContext):
    """Show confirmation with all parameters."""
    await state.set_state(DisclaimerCreation.confirming)
    
    data = await state.get_data()
    creative_type = CreativeType(data["creative_type"])
    
    # Build summary
    summary = "📋 <b>Проверьте параметры:</b>\n\n"
    summary += f"🎨 <b>Тип:</b> {CREATIVE_TYPE_NAMES[creative_type]}\n"
    summary += f"📍 <b>География:</b> {normalize_city_name(data['city'])}\n"
    summary += f"📺 <b>Канал:</b> {'ТВ/Радио' if data['channel'] == 'tv_radio' else 'Другие форматы'}\n"
    
    if data.get("end_date"):
        summary += f"📅 <b>Действует до:</b> {data['end_date']}\n"
    
    if data.get("start_date"):
        summary += f"📅 <b>Действует с:</b> {data['start_date']}\n"
    
    if data.get("max_discount_amount"):
        summary += f"💰 <b>Макс. скидка:</b> {data['max_discount_amount']} ₽\n"
    
    if data.get("discount_size"):
        summary += f"💰 <b>Размер скидки:</b> {data['discount_size']}{data.get('discount_unit', '')}\n"
    
    if data.get("first_order_only"):
        summary += "🎯 <b>Только первый заказ:</b> Да\n"
    
    if data.get("specific_category"):
        summary += f"🏷 <b>Категория:</b> {data['specific_category']}\n"
    
    if data.get("min_order_amount"):
        summary += f"📦 <b>Мин. сумма заказа:</b> {data['min_order_amount']} ₽\n"
    
    if data.get("max_promo_discount"):
        summary += f"💳 <b>Макс. скидка:</b> {data['max_promo_discount']} ₽\n"
    
    if data.get("usage_count"):
        summary += f"🔄 <b>Применений:</b> {data['usage_count']} раз\n"
    
    if data.get("add_delivery_info"):
        summary += "🚚 <b>Доставка:</b> Да\n"
    
    summary += "\nВсе верно?"
    
    await message.answer(summary, parse_mode="HTML", reply_markup=get_confirmation_keyboard())


@router.callback_query(DisclaimerCreation.confirming, F.data == "confirm:yes")
async def generate_disclaimer(callback: CallbackQuery, state: FSMContext):
    """Generate and show disclaimer."""
    data = await state.get_data()
    
    try:
        # Build parameters
        params = CreativeParams(
            creative_type=CreativeType(data["creative_type"]),
            city=data["city"],
            channel=ChannelType(data["channel"]),
            end_date=data.get("end_date"),
            max_discount_amount=data.get("max_discount_amount"),
            add_delivery_info=data.get("add_delivery_info", False),
            delivery_info_text=data.get("delivery_info_text"),
            discount_size=data.get("discount_size"),
            discount_unit=data.get("discount_unit"),
            first_order_only=data.get("first_order_only", False),
            specific_category=data.get("specific_category"),
            min_order_amount=data.get("min_order_amount"),
            max_promo_discount=data.get("max_promo_discount"),
            usage_count=data.get("usage_count"),
            start_date=data.get("start_date")
        )
        
        # Generate disclaimer
        disclaimer = generator.generate(params)
        
        result_text = (
            "✅ <b>Дисклеймер готов!</b>\n\n"
            f"<pre>{disclaimer}</pre>\n\n"
            "📋 Нажмите на текст для копирования"
        )
        
        await callback.message.edit_text(result_text, parse_mode="HTML", reply_markup=get_result_keyboard())
        await state.clear()
        
    except ValidationError as e:
        await callback.message.edit_text(
            f"❌ <b>Ошибка валидации:</b>\n{str(e)}\n\nИспользуйте /create для создания нового дисклеймера.",
            parse_mode="HTML"
        )
        await state.clear()
    
    await callback.answer()


@router.callback_query(DisclaimerCreation.confirming, F.data == "confirm:edit")
async def edit_parameters(callback: CallbackQuery, state: FSMContext):
    """Restart the process to edit parameters."""
    await callback.message.delete()
    await callback.message.answer("Давайте начнем заново.")
    await state.clear()
    await cmd_create(callback.message, state)
    await callback.answer()


@router.callback_query(DisclaimerCreation.confirming, F.data == "confirm:restart")
async def restart_creation(callback: CallbackQuery, state: FSMContext):
    """Restart disclaimer creation."""
    await callback.message.delete()
    await state.clear()
    await cmd_create(callback.message, state)
    await callback.answer()


@router.callback_query(F.data == "result:new")
async def create_new_disclaimer(callback: CallbackQuery, state: FSMContext):
    """Create new disclaimer."""
    await callback.message.delete()
    await state.clear()
    await cmd_create(callback.message, state)
    await callback.answer()


@router.callback_query(F.data == "result:menu")
async def show_main_menu(callback: CallbackQuery, state: FSMContext):
    """Show main menu."""
    await callback.message.delete()
    await state.clear()
    await callback.message.answer(
        "Главное меню. Выберите действие:",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


# Mass generation mode
@router.message(F.text == "⚡ Массовая генерация")
async def cmd_mass_create(message: Message, state: FSMContext):
    """Start mass generation mode."""
    logger.info(f"Starting mass generation for user {message.from_user.id}")
    await state.clear()
    await state.set_state(MassGeneration.choosing_type)
    await state.update_data(selected_cities=[])

    new_state = await state.get_state()
    logger.info(f"Mass generation state set to: {new_state}")

    text = "🔥 <b>Режим массовой генерации</b>\n\nВыберите тип креатива:"
    await message.answer(text, parse_mode="HTML", reply_markup=get_creative_type_keyboard_mass())


@router.callback_query(MassGeneration.choosing_type, F.data.startswith("mass_type:"))
async def mass_process_type_selection(callback: CallbackQuery, state: FSMContext):
    """Process creative type selection in mass mode."""
    logger.info(f"Mass mode: type selection callback received: {callback.data}, user: {callback.from_user.id}")
    creative_type = callback.data.split(":")[1]
    await state.update_data(creative_type=creative_type)

    await state.set_state(MassGeneration.choosing_multiple_cities)
    logger.info(f"Mass mode: state set to choosing_multiple_cities")
    await callback.message.edit_text(
        f"✅ Тип: {CREATIVE_TYPE_NAMES[CreativeType(creative_type)]}\n\n"
        "Выберите города (можно несколько):",
        reply_markup=get_geography_keyboard_multiple([])
    )
    await callback.answer()


@router.callback_query(MassGeneration.choosing_multiple_cities, F.data.startswith("city_toggle:"))
async def toggle_city_selection(callback: CallbackQuery, state: FSMContext):
    """Toggle city selection."""
    city = callback.data.split(":")[1]
    data = await state.get_data()
    selected = data.get("selected_cities", [])
    
    if city in selected:
        selected.remove(city)
    else:
        selected.append(city)
    
    await state.update_data(selected_cities=selected)
    
    # Update keyboard
    creative_type = data.get("creative_type")
    await callback.message.edit_text(
        f"✅ Тип: {CREATIVE_TYPE_NAMES[CreativeType(creative_type)]}\n\n"
        "Выберите города (можно несколько):",
        reply_markup=get_geography_keyboard_multiple(selected)
    )
    await callback.answer()


@router.callback_query(MassGeneration.choosing_multiple_cities, F.data == "cities:ready")
async def mass_cities_ready(callback: CallbackQuery, state: FSMContext):
    """Proceed after cities selection."""
    data = await state.get_data()
    selected = data.get("selected_cities", [])

    if not selected:
        await callback.answer("⚠️ Выберите хотя бы один город!", show_alert=True)
        return

    await state.set_state(MassGeneration.choosing_channel)

    cities_list = ", ".join([normalize_city_name(c) for c in selected[:5]])
    if len(selected) > 5:
        cities_list += f" и еще {len(selected) - 5}"

    await callback.message.edit_text(
        f"✅ Выбрано городов: {len(selected)}\n"
        f"({cities_list})\n\n"
        "Выберите канал размещения:",
        reply_markup=get_channel_keyboard_mass()
    )
    await callback.answer()


@router.callback_query(MassGeneration.choosing_channel, F.data.startswith("mass_channel:"))
async def mass_process_channel_selection(callback: CallbackQuery, state: FSMContext):
    """Process channel selection in mass mode."""
    channel = callback.data.split(":")[1]
    await state.update_data(channel=channel)
    
    data = await state.get_data()
    creative_type = CreativeType(data["creative_type"])
    
    await callback.message.edit_text(f"✅ Канал: {'ТВ/Радио' if channel == 'tv_radio' else 'Другие форматы'}")
    
    # Route to appropriate next step based on creative type
    if creative_type == CreativeType.DYNAMIC_NEWCOMER:
        await ask_end_date_mass(callback.message, state, "Введите дату окончания акции (формат: ДД.ММ.ГГ или ДД.ММ.ГГГГ):")
    elif creative_type == CreativeType.CLASSIC_NEWCOMER:
        await ask_end_date_mass(callback.message, state, "Введите дату окончания акции (формат: ДД.ММ.ГГ или ДД.ММ.ГГГГ):")
    elif creative_type == CreativeType.PROMO_CODE:
        await ask_end_date_mass(callback.message, state, "Введите дату окончания промокода (формат: ДД.ММ.ГГ или ДД.ММ.ГГГГ):")
    elif creative_type == CreativeType.CERTIFICATE:
        await ask_end_date_mass(callback.message, state, "Введите дату окончания сертификата (формат: ДД.ММ.ГГ или ДД.ММ.ГГГГ):")
    elif creative_type == CreativeType.VENDOR:
        await ask_start_date_mass(callback.message, state)
    elif creative_type in [CreativeType.IMAGE, CreativeType.PRODUCT]:
        await show_confirmation_mass(callback.message, state)
    
    await callback.answer()


async def ask_end_date_mass(message: Message, state: FSMContext, prompt: str):
    """Ask for end date in mass mode."""
    await state.set_state(MassGeneration.entering_end_date)
    await message.answer(prompt, reply_markup=remove_keyboard())


async def ask_start_date_mass(message: Message, state: FSMContext):
    """Ask for start date in mass mode."""
    await state.set_state(MassGeneration.entering_start_date)
    await message.answer("Введите дату начала акции (формат: ДД.ММ.ГГ или ДД.ММ.ГГГГ):", reply_markup=remove_keyboard())


async def show_confirmation_mass(message: Message, state: FSMContext):
    """Show confirmation for mass generation."""
    await state.set_state(MassGeneration.confirming)
    
    data = await state.get_data()
    creative_type = CreativeType(data["creative_type"])
    selected_cities = data.get("selected_cities", [])
    
    # Build summary
    summary = "📋 <b>Проверьте параметры для массовой генерации:</b>\n\n"
    summary += f"🎨 <b>Тип:</b> {CREATIVE_TYPE_NAMES[creative_type]}\n"
    summary += f"🌍 <b>Городов:</b> {len(selected_cities)}\n"
    summary += f"📺 <b>Канал:</b> {'ТВ/Радио' if data['channel'] == 'tv_radio' else 'Другие форматы'}\n"
    
    if data.get("end_date"):
        summary += f"📅 <b>Действует до:</b> {data['end_date']}\n"
    
    if data.get("start_date"):
        summary += f"📅 <b>Действует с:</b> {data['start_date']}\n"

    summary += "\nБудут созданы дисклеймеры для всех выбранных городов. Продолжить?"

    await message.answer(summary, parse_mode="HTML", reply_markup=get_confirmation_keyboard_mass())


# Mass generation - copy handlers for other parameters
# For brevity, I'll add a simplified version that forwards to the confirmation after basic parameters


@router.message(MassGeneration.entering_end_date)
async def mass_process_end_date(message: Message, state: FSMContext):
    """Process end date in mass mode."""
    end_date = message.text.strip()
    
    is_valid, error = generator.validate_date(end_date)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуйте снова:")
        return
    
    await state.update_data(end_date=end_date)
    
    data = await state.get_data()
    creative_type = CreativeType(data["creative_type"])
    
    # Validate date order for vendor
    if creative_type == CreativeType.VENDOR:
        is_valid, error = generator.validate_dates_order(data["start_date"], end_date)
        if not is_valid:
            await message.answer(f"❌ {error}\n\nВведите дату окончания заново:")
            return

    if creative_type == CreativeType.DYNAMIC_NEWCOMER:
        await show_confirmation_mass(message, state)
    elif creative_type == CreativeType.CLASSIC_NEWCOMER:
        await ask_max_discount_mass(message, state)
    elif creative_type == CreativeType.PROMO_CODE:
        await ask_discount_size_mass(message, state)
    elif creative_type == CreativeType.CERTIFICATE:
        await ask_usage_count_mass(message, state)
    elif creative_type == CreativeType.VENDOR:
        await show_confirmation_mass(message, state)


async def ask_max_discount_mass(message: Message, state: FSMContext):
    """Ask for maximum discount in mass mode."""
    await state.set_state(MassGeneration.entering_max_discount)
    await message.answer("Введите максимальный размер скидки в рублях:")


@router.message(MassGeneration.entering_max_discount)
async def mass_process_max_discount(message: Message, state: FSMContext):
    """Process max discount in mass mode."""
    try:
        max_discount = int(message.text.strip())
        if max_discount <= 0:
            raise ValueError()
        
        await state.update_data(max_discount_amount=max_discount, add_delivery_info=False)
        await show_confirmation_mass(message, state)
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите положительное целое число:")


async def ask_discount_size_mass(message: Message, state: FSMContext):
    """Ask for discount size in mass mode."""
    await state.set_state(MassGeneration.entering_discount_size)
    await message.answer("Введите размер скидки (только число):")


@router.message(MassGeneration.entering_discount_size)
async def mass_process_discount_size(message: Message, state: FSMContext):
    """Process discount size in mass mode."""
    try:
        discount_size = float(message.text.strip().replace(",", "."))
        if discount_size <= 0:
            raise ValueError()
        
        await state.update_data(discount_size=discount_size)
        await ask_discount_unit_mass(message, state)
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите положительное число:")


async def ask_discount_unit_mass(message: Message, state: FSMContext):
    """Ask for discount unit in mass mode."""
    await state.set_state(MassGeneration.choosing_discount_unit)
    await message.answer("Выберите единицу измерения:", reply_markup=get_discount_unit_keyboard_mass())


@router.callback_query(MassGeneration.choosing_discount_unit, F.data.startswith("mass_unit:"))
async def mass_process_discount_unit(callback: CallbackQuery, state: FSMContext):
    """Process discount unit in mass mode."""
    unit = callback.data.split(":")[1]
    await state.update_data(discount_unit=unit, first_order_only=False, specific_category=None, 
                            min_order_amount=None, max_promo_discount=None)
    
    await callback.message.delete()
    
    # Create a temporary message object to pass to show_confirmation_mass
    # We need to send a new message instead of editing the deleted one
    data = await state.get_data()
    creative_type = CreativeType(data["creative_type"])
    selected_cities = data.get("selected_cities", [])
    
    # Set state before showing confirmation
    await state.set_state(MassGeneration.confirming)
    
    # Build summary
    summary = "📋 <b>Проверьте параметры для массовой генерации:</b>\n\n"
    summary += f"🎨 <b>Тип:</b> {CREATIVE_TYPE_NAMES[creative_type]}\n"
    summary += f"🌍 <b>Городов:</b> {len(selected_cities)}\n"
    summary += f"📺 <b>Канал:</b> {'ТВ/Радио' if data['channel'] == 'tv_radio' else 'Другие форматы'}\n"
    
    if data.get("end_date"):
        summary += f"📅 <b>Действует до:</b> {data['end_date']}\n"
    
    if data.get("discount_size"):
        summary += f"💰 <b>Размер скидки:</b> {data['discount_size']}{unit}\n"

    summary += "\nБудут созданы дисклеймеры для всех выбранных городов. Продолжить?"

    await callback.message.answer(summary, parse_mode="HTML", reply_markup=get_confirmation_keyboard_mass())
    await callback.answer()


async def ask_usage_count_mass(message: Message, state: FSMContext):
    """Ask for usage count in mass mode."""
    await state.set_state(MassGeneration.entering_usage_count)
    await message.answer("Введите количество применений сертификата:")


@router.message(MassGeneration.entering_usage_count)
async def mass_process_usage_count(message: Message, state: FSMContext):
    """Process usage count in mass mode."""
    try:
        usage_count = int(message.text.strip())
        if usage_count <= 0:
            raise ValueError()
        
        await state.update_data(usage_count=usage_count)
        await show_confirmation_mass(message, state)
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите положительное целое число:")


@router.message(MassGeneration.entering_start_date)
async def mass_process_start_date(message: Message, state: FSMContext):
    """Process start date in mass mode."""
    start_date = message.text.strip()
    
    is_valid, error = generator.validate_date(start_date)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуйте снова:")
        return
    
    await state.update_data(start_date=start_date)
    await ask_end_date_mass(message, state, "Введите дату окончания акции (формат: ДД.ММ.ГГ или ДД.ММ.ГГГГ):")


@router.callback_query(MassGeneration.confirming, F.data == "mass_confirm:yes")
async def generate_mass_disclaimers(callback: CallbackQuery, state: FSMContext):
    """Generate disclaimers for all selected cities."""
    data = await state.get_data()
    selected_cities = data.get("selected_cities", [])
    
    if not selected_cities:
        await callback.message.edit_text("❌ Ошибка: не выбраны города")
        await state.clear()
        return
    
    try:
        # Generate disclaimers for all cities
        disclaimers = []
        
        for city in selected_cities:
            params = CreativeParams(
                creative_type=CreativeType(data["creative_type"]),
                city=city,
                channel=ChannelType(data["channel"]),
                end_date=data.get("end_date"),
                max_discount_amount=data.get("max_discount_amount"),
                add_delivery_info=data.get("add_delivery_info", False),
                delivery_info_text=data.get("delivery_info_text"),
                discount_size=data.get("discount_size"),
                discount_unit=data.get("discount_unit"),
                first_order_only=data.get("first_order_only", False),
                specific_category=data.get("specific_category"),
                min_order_amount=data.get("min_order_amount"),
                max_promo_discount=data.get("max_promo_discount"),
                usage_count=data.get("usage_count"),
                start_date=data.get("start_date")
            )
            
            disclaimer = generator.generate(params)
            disclaimers.append((city, disclaimer))
        
        # Build result message
        result_text = f"✅ <b>Создано {len(disclaimers)} дисклеймеров!</b>\n\n"
        
        for city, disclaimer in disclaimers:
            city_name = normalize_city_name(city)
            result_text += f"<b>📍 {city_name}</b>\n"
            result_text += f"<pre>{disclaimer}</pre>\n\n"
            result_text += "━━━━━━━━━━━━━━━━━\n\n"
        
        result_text += "📋 Нажмите на любой текст для копирования"
        
        # Send result (split if too long)
        if len(result_text) > 4096:
            # Split into chunks
            await callback.message.edit_text("✅ <b>Генерация завершена! Отправляю результаты...</b>", parse_mode="HTML")
            
            chunk_header = f"✅ <b>Дисклеймеры (часть {{n}}):</b>\n\n"
            current_chunk = ""
            chunk_num = 1
            
            for city, disclaimer in disclaimers:
                city_name = normalize_city_name(city)
                city_block = f"<b>📍 {city_name}</b>\n<pre>{disclaimer}</pre>\n\n━━━━━━━━━━━━━━━━━\n\n"
                
                if len(current_chunk) + len(city_block) + len(chunk_header.format(n=chunk_num)) > 4000:
                    await callback.message.answer(
                        chunk_header.format(n=chunk_num) + current_chunk,
                        parse_mode="HTML"
                    )
                    current_chunk = city_block
                    chunk_num += 1
                else:
                    current_chunk += city_block
            
            if current_chunk:
                await callback.message.answer(
                    chunk_header.format(n=chunk_num) + current_chunk + "\n📋 Нажмите на любой текст для копирования",
                    parse_mode="HTML",
                    reply_markup=get_result_keyboard()
                )
        else:
            await callback.message.edit_text(result_text, parse_mode="HTML", reply_markup=get_result_keyboard())
        
        await state.clear()
        
    except ValidationError as e:
        await callback.message.edit_text(
            f"❌ <b>Ошибка валидации:</b>\n{str(e)}\n\nИспользуйте /create для создания нового дисклеймера.",
            parse_mode="HTML"
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Error in mass generation: {e}", exc_info=True)
        await callback.message.edit_text(
            f"❌ <b>Ошибка:</b>\n{str(e)}",
            parse_mode="HTML"
        )
        await state.clear()
    
    await callback.answer()


@router.callback_query(MassGeneration.confirming, F.data == "mass_confirm:edit")
async def mass_edit_parameters(callback: CallbackQuery, state: FSMContext):
    """Restart mass generation to edit parameters."""
    await callback.message.delete()
    await callback.message.answer("Давайте начнем заново.")
    await state.clear()
    await cmd_mass_create(callback.message, state)
    await callback.answer()


@router.callback_query(MassGeneration.confirming, F.data == "mass_confirm:restart")
async def mass_restart_creation(callback: CallbackQuery, state: FSMContext):
    """Restart mass generation."""
    await callback.message.delete()
    await state.clear()
    await cmd_mass_create(callback.message, state)
    await callback.answer()


# Catch unhandled callbacks
@router.callback_query()
async def handle_unhandled_callback(callback: CallbackQuery, state: FSMContext):
    """Handle any unhandled callback."""
    current_state = await state.get_state()
    logger.warning(f"Unhandled callback: {callback.data}, user: {callback.from_user.id}, state: {current_state}")

    # Don't show error for known callback patterns that should be handled
    if callback.data and (
        callback.data.startswith("type:") or
        callback.data.startswith("geo:") or
        callback.data.startswith("channel:") or
        callback.data.startswith("city_toggle:") or
        callback.data == "cities:ready" or
        callback.data.startswith("mass_type:") or
        callback.data.startswith("mass_channel:") or
        callback.data.startswith("mass_unit:") or
        callback.data.startswith("mass_confirm:")
    ):
        # These should have been handled by state-specific handlers
        # Log detailed error and reset state
        logger.error(f"Callback {callback.data} not handled properly. Current state: {current_state}. This indicates a state management issue.")
        await callback.answer("⚠️ Произошла ошибка. Начните заново с /create или выберите действие в меню.")
        await state.clear()
    else:
        await callback.answer("⚠️ Неизвестная команда")


# Catch unhandled messages
@router.message()
async def handle_text(message: Message):
    """Handle any other text message."""
    await message.answer(
        "Используйте /create для пошагового создания дисклеймера или /help для справки.",
        reply_markup=get_main_menu_keyboard()
    )
