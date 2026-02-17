"""Disclaimer generator with validation logic."""
import re
from datetime import datetime
from typing import Optional, Tuple
from models import (
    CreativeType,
    CreativeParams,
    ChannelType,
    get_legal_entity,
    is_mo,
    ALL_CITIES
)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class DisclaimerGenerator:
    """Generator for Yandex Lavka disclaimers."""
    
    # Links
    LINK_MO = "clck.ru/397gmg"
    LINK_CITIES = "clck.ru/3Dq8fF"
    
    # Standard texts
    EXCLUDED_CATEGORIES = '«Сертификаты», «Магазин Яндекса» и «Магазины по пути»'
    PROMO_EXCLUDED = '«Магазин Яндекса», «Товары для взрослых», «Сертификаты», «Молочные смеси», товары с доставкой «По пути», «Аптеки»'
    NO_COMBINATION = "Не суммируется с другими акциями."
    CERTIFICATE_RULE = "Если номинал сертификата покрывает полностью стоимость заказа, то сумма каждой единицы товара, оплачиваемых пользователем, с учетом скидки будет равна 1 (одному) рублю."
    CERTIFICATE_LINK = "https://yandex.ru/legal/promocode_eda/"
    LIMITED_QUANTITY = "Количество товаров ограничено."
    DELIVERY_NOT_INCLUDED = "Не применяется на стоимость доставки и упаковки."
    DEFAULT_DELIVERY_INFO = "Три бесплатные доставки в пешей и одна в авто зоне. Доставку осуществляют партнеры Яндекс Еды."
    
    @staticmethod
    def validate_date(date_str: str) -> Tuple[bool, Optional[str]]:
        """
        Validate date format DD.MM.YY or DD.MM.YYYY.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not date_str:
            return False, "Дата не указана"
        
        # Support both 2-digit and 4-digit year formats
        pattern = r'^(\d{2})\.(\d{2})\.(\d{2}|\d{4})$'
        match = re.match(pattern, date_str)
        
        if not match:
            return False, f"Неверный формат даты. Используйте ДД.ММ.ГГ или ДД.ММ.ГГГГ (например, 31.12.24 или 31.12.2024)"
        
        day, month, year_str = match.groups()
        day, month = int(day), int(month)
        
        # Validate ranges
        if not (1 <= month <= 12):
            return False, "Месяц должен быть от 01 до 12"
        
        if not (1 <= day <= 31):
            return False, "День должен быть от 01 до 31"
        
        # Basic day validation for month
        if month in [4, 6, 9, 11] and day > 30:
            return False, f"В месяце {month:02d} не может быть {day} дней"
        
        if month == 2 and day > 29:
            return False, "В феврале не может быть больше 29 дней"
        
        return True, None
    
    @staticmethod
    def validate_city(city: str) -> Tuple[bool, Optional[str]]:
        """Validate city name."""
        if not city:
            return False, "Город не указан"
        
        city_lower = city.lower().strip()
        if city_lower not in [c.lower() for c in ALL_CITIES]:
            return False, f"Город '{city}' не найден в списке доступных городов"
        
        return True, None
    
    @staticmethod
    def validate_positive_number(value: Optional[float], field_name: str) -> Tuple[bool, Optional[str]]:
        """Validate positive number."""
        if value is None:
            return True, None  # Optional field
        
        if value <= 0:
            return False, f"{field_name} должно быть положительным числом"
        
        return True, None
    
    @staticmethod
    def validate_percentage(value: Optional[float]) -> Tuple[bool, Optional[str]]:
        """Validate percentage value."""
        if value is None:
            return True, None
        
        if not (0 < value <= 100):
            return False, "Процент должен быть от 0 до 100"
        
        return True, None
    
    @staticmethod
    def validate_dates_order(start_date: str, end_date: str) -> Tuple[bool, Optional[str]]:
        """Validate that start date is before end date."""
        try:
            # Normalize dates to handle both YY and YYYY formats
            def parse_flexible_date(date_str: str) -> datetime:
                """Parse date with flexible year format."""
                parts = date_str.split('.')
                if len(parts) != 3:
                    raise ValueError("Invalid date format")
                
                day, month, year = parts
                # If year is 2 digits, use %y, otherwise use %Y
                if len(year) == 2:
                    return datetime.strptime(date_str, "%d.%m.%y")
                elif len(year) == 4:
                    return datetime.strptime(date_str, "%d.%m.%Y")
                else:
                    raise ValueError("Year must be 2 or 4 digits")
            
            start = parse_flexible_date(start_date)
            end = parse_flexible_date(end_date)
            
            if start >= end:
                return False, "Дата начала должна быть раньше даты окончания"
            
            return True, None
        except ValueError:
            return False, "Ошибка при сравнении дат"
    
    def validate_params(self, params: CreativeParams) -> Tuple[bool, Optional[str]]:
        """
        Validate all parameters for a creative type.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate city
        is_valid, error = self.validate_city(params.city)
        if not is_valid:
            return False, error
        
        # Type-specific validation
        if params.creative_type == CreativeType.DYNAMIC_NEWCOMER:
            return self._validate_dynamic_newcomer(params)
        elif params.creative_type == CreativeType.CLASSIC_NEWCOMER:
            return self._validate_classic_newcomer(params)
        elif params.creative_type == CreativeType.PROMO_CODE:
            return self._validate_promo_code(params)
        elif params.creative_type == CreativeType.CERTIFICATE:
            return self._validate_certificate(params)
        elif params.creative_type == CreativeType.VENDOR:
            return self._validate_vendor(params)
        elif params.creative_type in [CreativeType.IMAGE, CreativeType.PRODUCT]:
            return True, None  # No additional validation needed
        
        return True, None
    
    def _validate_dynamic_newcomer(self, params: CreativeParams) -> Tuple[bool, Optional[str]]:
        """Validate dynamic newcomer discount parameters."""
        if not params.end_date:
            return False, "Дата окончания обязательна"
        
        return self.validate_date(params.end_date)
    
    def _validate_classic_newcomer(self, params: CreativeParams) -> Tuple[bool, Optional[str]]:
        """Validate classic newcomer discount parameters."""
        if not params.end_date:
            return False, "Дата окончания обязательна"
        
        is_valid, error = self.validate_date(params.end_date)
        if not is_valid:
            return False, error
        
        if not params.max_discount_amount:
            return False, "Максимальный размер скидки обязателен"
        
        return self.validate_positive_number(params.max_discount_amount, "Максимальный размер скидки")
    
    def _validate_promo_code(self, params: CreativeParams) -> Tuple[bool, Optional[str]]:
        """Validate promo code parameters."""
        if not params.end_date:
            return False, "Дата окончания обязательна"
        
        is_valid, error = self.validate_date(params.end_date)
        if not is_valid:
            return False, error
        
        if not params.discount_size:
            return False, "Размер скидки обязателен"
        
        if not params.discount_unit or params.discount_unit not in ["%", "₽"]:
            return False, "Единица измерения скидки должна быть % или ₽"
        
        if params.discount_unit == "%":
            is_valid, error = self.validate_percentage(params.discount_size)
            if not is_valid:
                return False, error
        else:
            is_valid, error = self.validate_positive_number(params.discount_size, "Размер скидки")
            if not is_valid:
                return False, error
        
        # Validate optional fields
        is_valid, error = self.validate_positive_number(params.min_order_amount, "Минимальная сумма заказа")
        if not is_valid:
            return False, error
        
        is_valid, error = self.validate_positive_number(params.max_promo_discount, "Максимальная скидка")
        if not is_valid:
            return False, error
        
        return True, None
    
    def _validate_certificate(self, params: CreativeParams) -> Tuple[bool, Optional[str]]:
        """Validate certificate parameters."""
        if not params.end_date:
            return False, "Дата окончания обязательна"
        
        is_valid, error = self.validate_date(params.end_date)
        if not is_valid:
            return False, error
        
        if not params.usage_count:
            return False, "Количество применений обязательно"
        
        if params.usage_count <= 0 or not isinstance(params.usage_count, int):
            return False, "Количество применений должно быть целым положительным числом"
        
        return True, None
    
    def _validate_vendor(self, params: CreativeParams) -> Tuple[bool, Optional[str]]:
        """Validate vendor creative parameters."""
        if not params.start_date:
            return False, "Дата начала обязательна"
        
        if not params.end_date:
            return False, "Дата окончания обязательна"
        
        is_valid, error = self.validate_date(params.start_date)
        if not is_valid:
            return False, f"Дата начала: {error}"
        
        is_valid, error = self.validate_date(params.end_date)
        if not is_valid:
            return False, f"Дата окончания: {error}"
        
        return self.validate_dates_order(params.start_date, params.end_date)
    
    def generate(self, params: CreativeParams) -> str:
        """
        Generate disclaimer based on parameters.
        
        Raises:
            ValidationError: If parameters are invalid
        """
        # Validate parameters
        is_valid, error = self.validate_params(params)
        if not is_valid:
            raise ValidationError(error)
        
        # Get legal entity
        legal_entity = get_legal_entity(params.city, params.channel)
        
        # Generate based on type
        if params.creative_type == CreativeType.DYNAMIC_NEWCOMER:
            return self._generate_dynamic_newcomer(params, legal_entity)
        elif params.creative_type == CreativeType.CLASSIC_NEWCOMER:
            return self._generate_classic_newcomer(params, legal_entity)
        elif params.creative_type == CreativeType.PROMO_CODE:
            return self._generate_promo_code(params, legal_entity)
        elif params.creative_type == CreativeType.CERTIFICATE:
            return self._generate_certificate(params, legal_entity)
        elif params.creative_type == CreativeType.IMAGE:
            return self._generate_image(legal_entity)
        elif params.creative_type == CreativeType.PRODUCT:
            return self._generate_product(legal_entity)
        elif params.creative_type == CreativeType.VENDOR:
            return self._generate_vendor(params, legal_entity)
        
        raise ValidationError(f"Неизвестный тип креатива: {params.creative_type}")
    
    def _generate_dynamic_newcomer(self, params: CreativeParams, legal_entity: str) -> str:
        """Generate dynamic newcomer discount disclaimer."""
        link = self.LINK_MO  # Always MO for dynamic
        
        disclaimer = (
            f"Акция действует до {params.end_date}. "
            f"Не распространяется на категории {self.EXCLUDED_CATEGORIES}. "
            f"Подробности - {link}. "
            f"{legal_entity}."
        )
        
        return disclaimer
    
    def _generate_classic_newcomer(self, params: CreativeParams, legal_entity: str) -> str:
        """Generate classic newcomer discount disclaimer."""
        link = self.LINK_CITIES
        
        disclaimer = (
            f"Акция действует до {params.end_date} "
            f"(максимальный размер скидки - {params.max_discount_amount} руб.). "
            f"Не распространяется на категории {self.EXCLUDED_CATEGORIES}. "
            f"Подробности - {link}. "
        )
        
        # Add delivery info if needed
        if params.add_delivery_info:
            delivery_text = params.delivery_info_text or self.DEFAULT_DELIVERY_INFO
            disclaimer += f"{delivery_text}"
        
        disclaimer += f"{legal_entity}"
        
        return disclaimer
    
    def _generate_promo_code(self, params: CreativeParams, legal_entity: str) -> str:
        """Generate promo code disclaimer."""
        # Build discount text
        discount_text = f"скидка {params.discount_size}{params.discount_unit}"
        
        # Build conditions text
        conditions = []
        
        if params.first_order_only:
            conditions.append("на первый заказ")
        elif params.specific_category:
            conditions.append(f'на заказ из категорий "{params.specific_category}"')
        
        if params.min_order_amount:
            conditions.append(f"от {params.min_order_amount} ₽")
        
        # Don't add "не более X ₽" if discount is already in rubles (to avoid duplication)
        if params.max_promo_discount and params.discount_unit != "₽":
            conditions.append(f"не более {params.max_promo_discount} ₽")
        
        conditions_text = " ".join(conditions)
        if conditions_text:
            discount_text += f" {conditions_text}"
        
        disclaimer = (
            f"До {params.end_date} {discount_text}. "
            f"Не применяется к товарам из разделов {self.PROMO_EXCLUDED}. "
            f"{self.NO_COMBINATION} "
            f"{legal_entity}"
        )
        
        return disclaimer
    
    def _generate_certificate(self, params: CreativeParams, legal_entity: str) -> str:
        """Generate certificate disclaimer."""
        disclaimer = (
            f"Сертификат действует до {params.end_date}. "
            f"Количество применений сертификата - не более {params.usage_count} раз "
            f"в пределах номинала сертификата. "
            f"{self.CERTIFICATE_RULE} "
            f"Подробные условия применения - {self.CERTIFICATE_LINK}. "
            f"{self.DELIVERY_NOT_INCLUDED} "
            f"{legal_entity}"
        )
        
        return disclaimer
    
    def _generate_image(self, legal_entity: str) -> str:
        """Generate image creative disclaimer."""
        return f"{legal_entity}"
    
    def _generate_product(self, legal_entity: str) -> str:
        """Generate product creative disclaimer."""
        return f"{self.LIMITED_QUANTITY} {legal_entity}"
    
    def _generate_vendor(self, params: CreativeParams, legal_entity: str) -> str:
        """Generate vendor creative disclaimer."""
        disclaimer = (
            f"Акция действует с {params.start_date} по {params.end_date}. "
            f"{self.LIMITED_QUANTITY} "
            f"{legal_entity}"
        )
        
        return disclaimer
