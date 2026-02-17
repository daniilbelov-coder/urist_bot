"""Data models for legal entities, cities, and creative types."""
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class CreativeType(str, Enum):
    """Types of creatives."""
    DYNAMIC_NEWCOMER = "dynamic_newcomer"
    CLASSIC_NEWCOMER = "classic_newcomer"
    PROMO_CODE = "promo_code"
    CERTIFICATE = "certificate"
    IMAGE = "image"
    PRODUCT = "product"
    VENDOR = "vendor"


class ChannelType(str, Enum):
    """Channel types for placement."""
    TV_RADIO = "tv_radio"
    OTHER = "other"


@dataclass
class LegalEntity:
    """Legal entity information."""
    short: str
    full: str


# Yandex Lavka legal entity
YANDEX_LAVKA = LegalEntity(
    short="ООО «Яндекс Лавка», Москва, ОГРН 1187746479250",
    full="ООО «Яндекс.Лавка», 123112, г. Москва, пр. 1-й Красногвардейский, д. 22, стр. 1, эт. 12, пом. 12-40, ОГРН 1187746479250"
)

# Franchise legal entities by city
FRANCHISE_ENTITIES: Dict[str, LegalEntity] = {
    "тула": LegalEntity(
        short="ООО «Лавка Счастья», Липецк, ОГРН 1234800004878",
        full="ООО «Лавка Счастья» (398059, г. Липецк, ул. Коммунальная, д. 3, помещ. 1, ОГРН 1234800004878)"
    ),
    "тверь": LegalEntity(
        short="ООО «ДВМ-ГРУПП», Тверь, ОГРН 1246900009850",
        full="ООО «ДВМ-ГРУПП» (170100, г. Тверь, б-р Радищева, д. 12, этаж 2 помещ. 15, ОГРН 1246900009850)"
    ),
    "ярославль": LegalEntity(
        short="ООО «ЯРЛАВКА», Ярославль, ОГРН 1257600001845",
        full="ООО «ЯРЛАВКА» (150007, г. Ярославль, Сквозной переулок, д. 8А, кв. 3, ОГРН 1257600001845)"
    ),
    "рязань": LegalEntity(
        short="ООО «Лавка Радости», Липецк, ОГРН 1254800002049",
        full="ООО «Лавка Радости» (398059, Липецкая область, г. Липецк, ул. Коммунальная, д. 3, помещ. 1, ОГРН 1254800002049)"
    ),
    "калуга": LegalEntity(
        short="ООО «ГОССТРОЙРЕСУРС», Калуга, ОГРН 1154028002688",
        full="ООО «ГОССТРОЙРЕСУРС» (248001, Калужская область, г Калуга, ул Суворова, д. 17, ОГРН 1154028002688)"
    ),
    "великий новгород": LegalEntity(
        short="ООО «Премиум Стор», рп Панковка, ОГРН 1157847202996",
        full="ООО «Премиум Стор» (173526, Новгородская область, рп Панковка, ул. Строительная, д. 7Б, офис 1Б, ОГРН 1157847202996)"
    ),
    "обнинск": LegalEntity(
        short="ООО «ЛАВКАГОУ», Санкт-Петербург, ОГРН 1257800045051",
        full="ООО «ЛАВКАГОУ» (197376, г. Санкт-Петербург, ул. Планерная, д. 99 стр.1, помещ. 47Н, ОГРН 1257800045051)"
    ),
    "липецк": LegalEntity(
        short="ООО «АМР», Липецкая область, м.о. Липецкий, с. Сырское, ОГРН 1254800003875",
        full="ООО «АМР» (Липецкая обл., М.О. Липецкий, с. Сырское, ул. Воронежская, стр. 35, помещ. 11, ОГРН 1254800003875)"
    ),
    "иваново": LegalEntity(
        short="ООО «ИВЛАВКА», Иваново, ОГРН 1253700005591",
        full="ООО «ИВЛАВКА» (153000, Ивановская область, г. Иваново, ул. Палехская, д. 6., ОГРН 1253700005591)"
    ),
    "тамбов": LegalEntity(
        short="ООО «Лавка мечты», Липецк, ОГРН 1254800004700",
        full="ООО «Лавка мечты» (398001, г. Липецк, ул Л. Толстого, д. 7, помещ. 2, ОГРН 1254800004700)"
    ),
    "владимир": LegalEntity(
        short="ООО «ДВМ-ГРУПП», Тверь, ОГРН 1246900009850",
        full="ООО «ДВМ-ГРУПП» (170100, г. Тверь, б-р Радищева, д. 12, этаж 2 помещ. 15, ОГРН 1246900009850)"
    ),
    "иркутск": LegalEntity(
        short="ООО «ПРОДСНАБ», Иркутск, ОГРН 1213800013250",
        full="ООО «ПРОДСНАБ» (664035, Иркутская обл., г. Иркутск, ул. Рабочего штаба, д. 15, помещ. 6, ОГРН 1213800013250)"
    ),
    "набережные челны": LegalEntity(
        short="ООО «Премиум Стор», рп Панковка, ОГРН 1157847202996",
        full="ООО «Премиум Стор» (173526, Новгородская область, рп Панковка, ул. Строительная, д. 7Б, офис 1Б, ОГРН 1157847202996)"
    ),
    "нижнекамск": LegalEntity(
        short="ООО «Премиум Стор», рп Панковка, ОГРН 1157847202996",
        full="ООО «Премиум Стор» (173526, Новгородская область, рп Панковка, ул. Строительная, д. 7Б, офис 1Б, ОГРН 1157847202996)"
    ),
    "чебоксары": LegalEntity(
        short="ООО «Сервисная франшиза магазинов и кафе», Москва, ОГРН 1237700294138",
        full="ООО «Сервисная франшиза магазинов и кафе» (123007,г. Москва, проезд 3-й Хорошевский, д. 1 стр. 1, помещ. 3/1, ОГРН 1237700294138)"
    ),
    "йошкар-ола": LegalEntity(
        short="ООО «Сервисная франшиза магазинов и кафе», Москва, ОГРН 1237700294138",
        full="ООО «Сервисная франшиза магазинов и кафе» (123007,г. Москва, проезд 3-й Хорошевский, д. 1 стр. 1, помещ. 3/1, ОГРН 1237700294138)"
    ),
}

# Corporate cities use Yandex Lavka entity
CORPORATE_CITIES = [
    "москва",
    "мо",
    "московская область",
    "санкт-петербург",
    "спб",
    "ло",
    "ленинградская область",
    "казань",
    "новосибирск",
    "нижний новгород",
    "ростов",
    "краснодар",
    "екатеринбург",
    "челябинск",
    "тюмень",
    "сочи",
    "воронеж",
    "пермь"
]

# All available cities
ALL_CITIES = CORPORATE_CITIES + list(FRANCHISE_ENTITIES.keys())


def get_legal_entity(city: str, channel: ChannelType) -> str:
    """Get legal entity text for a city and channel."""
    city_lower = city.lower().strip()
    
    # Determine which entity to use
    if city_lower in CORPORATE_CITIES:
        entity = YANDEX_LAVKA
    elif city_lower in FRANCHISE_ENTITIES:
        entity = FRANCHISE_ENTITIES[city_lower]
    else:
        raise ValueError(f"Город '{city}' не найден в списке доступных городов")
    
    # Return appropriate version based on channel
    if channel == ChannelType.TV_RADIO:
        return entity.full
    else:
        return entity.short


def is_mo(city: str) -> bool:
    """Check if the city is MO (Moscow Oblast)."""
    city_lower = city.lower().strip()
    return city_lower in ["мо", "московская область"]


def normalize_city_name(city: str) -> str:
    """Normalize city name for display."""
    city_lower = city.lower().strip()
    
    # Special cases
    if city_lower in ["мо", "московская область"]:
        return "МО"
    if city_lower in ["спб", "санкт-петербург"]:
        return "Санкт-Петербург"
    if city_lower in ["ло", "ленинградская область"]:
        return "Ленинградская область"
    
    # Capitalize first letter
    return city.strip().capitalize()


@dataclass
class CreativeParams:
    """Parameters for disclaimer generation."""
    creative_type: CreativeType
    city: str
    channel: ChannelType
    
    # Common fields
    end_date: Optional[str] = None
    
    # Newcomer discount specific
    max_discount_amount: Optional[int] = None
    add_delivery_info: bool = False
    delivery_info_text: Optional[str] = None
    
    # Promo code specific
    discount_size: Optional[float] = None
    discount_unit: Optional[str] = None  # "%" or "₽"
    first_order_only: bool = False
    specific_category: Optional[str] = None
    min_order_amount: Optional[int] = None
    max_promo_discount: Optional[int] = None
    
    # Certificate specific
    usage_count: Optional[int] = None
    
    # Vendor specific
    start_date: Optional[str] = None


# Creative type display names
CREATIVE_TYPE_NAMES = {
    CreativeType.DYNAMIC_NEWCOMER: "Скидка новичка (динамическая)",
    CreativeType.CLASSIC_NEWCOMER: "Скидка новичка (классическая)",
    CreativeType.PROMO_CODE: "Промокод",
    CreativeType.CERTIFICATE: "Сертификат",
    CreativeType.IMAGE: "Имиджевый креатив",
    CreativeType.PRODUCT: "Продуктовый креатив",
    CreativeType.VENDOR: "Вендорский креатив",
}

# Channel display names
CHANNEL_NAMES = {
    ChannelType.TV_RADIO: "ТВ/Радио (полная версия юр.лица)",
    ChannelType.OTHER: "Другие форматы (короткая версия)",
}
