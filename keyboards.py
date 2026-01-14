"""Keyboard builders for the bot."""
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from models import CreativeType, ChannelType, CREATIVE_TYPE_NAMES, CHANNEL_NAMES, CORPORATE_CITIES, FRANCHISE_ENTITIES


def get_creative_type_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for selecting creative type."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="1️⃣ Скидка новичка (динамическая)", callback_data="type:dynamic_newcomer")
    builder.button(text="2️⃣ Скидка новичка (классическая)", callback_data="type:classic_newcomer")
    builder.button(text="3️⃣ Промокод", callback_data="type:promo_code")
    builder.button(text="4️⃣ Сертификат", callback_data="type:certificate")
    builder.button(text="5️⃣ Имиджевый", callback_data="type:image")
    builder.button(text="6️⃣ Продуктовый", callback_data="type:product")
    builder.button(text="7️⃣ Вендорский", callback_data="type:vendor")
    
    builder.adjust(1)
    return builder.as_markup()


def get_geography_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for selecting geography."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🏙 МО (Московская область)", callback_data="geo:мо")
    
    # Corporate cities
    builder.button(text="📍 Москва", callback_data="geo:москва")
    builder.button(text="📍 Санкт-Петербург", callback_data="geo:санкт-петербург")
    builder.button(text="📍 Казань", callback_data="geo:казань")
    builder.button(text="📍 Новосибирск", callback_data="geo:новосибирск")
    builder.button(text="📍 Нижний Новгород", callback_data="geo:нижний новгород")
    builder.button(text="📍 Ростов", callback_data="geo:ростов")
    builder.button(text="📍 Краснодар", callback_data="geo:краснодар")
    builder.button(text="📍 Екатеринбург", callback_data="geo:екатеринбург")
    builder.button(text="📍 Челябинск", callback_data="geo:челябинск")
    builder.button(text="📍 Тюмень", callback_data="geo:тюмень")
    builder.button(text="📍 Сочи", callback_data="geo:сочи")
    builder.button(text="📍 Воронеж", callback_data="geo:воронеж")
    builder.button(text="📍 Пермь", callback_data="geo:пермь")
    
    # Franchise cities
    builder.button(text="🏪 Тула", callback_data="geo:тула")
    builder.button(text="🏪 Тверь", callback_data="geo:тверь")
    builder.button(text="🏪 Ярославль", callback_data="geo:ярославль")
    builder.button(text="🏪 Рязань", callback_data="geo:рязань")
    builder.button(text="🏪 Калуга", callback_data="geo:калуга")
    builder.button(text="🏪 Великий Новгород", callback_data="geo:великий новгород")
    builder.button(text="🏪 Обнинск", callback_data="geo:обнинск")
    builder.button(text="🏪 Липецк", callback_data="geo:липецк")
    builder.button(text="🏪 Иваново", callback_data="geo:иваново")
    builder.button(text="🏪 Тамбов", callback_data="geo:тамбов")
    builder.button(text="🏪 Владимир", callback_data="geo:владимир")
    builder.button(text="🏪 Иркутск", callback_data="geo:иркутск")
    
    builder.adjust(2)
    return builder.as_markup()


def get_channel_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for selecting channel."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📺 ТВ/Радио (полная версия)", callback_data="channel:tv_radio")
    builder.button(text="🌐 Другие форматы (короткая версия)", callback_data="channel:other")
    
    builder.adjust(1)
    return builder.as_markup()


def get_yes_no_keyboard(yes_callback: str, no_callback: str) -> InlineKeyboardMarkup:
    """Get yes/no keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="✅ Да", callback_data=yes_callback)
    builder.button(text="❌ Нет", callback_data=no_callback)
    
    builder.adjust(2)
    return builder.as_markup()


def get_discount_unit_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for selecting discount unit."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="% Проценты", callback_data="unit:%")
    builder.button(text="₽ Рубли", callback_data="unit:₽")
    
    builder.adjust(2)
    return builder.as_markup()


def get_skip_keyboard(callback_data: str) -> InlineKeyboardMarkup:
    """Get skip button keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text="⏭ Пропустить", callback_data=callback_data)
    return builder.as_markup()


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Get confirmation keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="✅ Да, генерировать", callback_data="confirm:yes")
    builder.button(text="✏️ Изменить параметры", callback_data="confirm:edit")
    builder.button(text="🔄 Начать заново", callback_data="confirm:restart")
    
    builder.adjust(1)
    return builder.as_markup()


def get_result_keyboard() -> InlineKeyboardMarkup:
    """Get result actions keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🔄 Создать новый", callback_data="result:new")
    builder.button(text="📋 Главное меню", callback_data="result:menu")
    
    builder.adjust(1)
    return builder.as_markup()


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Get main menu keyboard."""
    builder = ReplyKeyboardBuilder()
    
    builder.button(text="➕ Создать дисклеймер")
    builder.button(text="❓ Помощь")
    
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def remove_keyboard() -> ReplyKeyboardRemove:
    """Remove keyboard."""
    return ReplyKeyboardRemove()
