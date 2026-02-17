"""FSM states for bot conversation."""
from aiogram.fsm.state import State, StatesGroup


class DisclaimerCreation(StatesGroup):
    """States for step-by-step disclaimer creation."""
    choosing_scenario = State()  # New: scenario selection (single/multiple)
    choosing_type = State()
    choosing_geography = State()
    choosing_multiple_geography = State()  # New: multiple cities selection
    choosing_channel = State()
    entering_end_date = State()
    entering_max_discount = State()
    choosing_delivery_info = State()
    entering_delivery_text = State()
    entering_discount_size = State()
    choosing_discount_unit = State()
    choosing_first_order = State()
    choosing_category = State()
    entering_category_name = State()
    entering_min_amount = State()
    entering_max_discount_promo = State()
    entering_usage_count = State()
    entering_start_date = State()
    confirming = State()
