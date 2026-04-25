from __future__ import annotations

from dataclasses import dataclass
import os

from dotenv import load_dotenv

DEFAULT_REPLY_TEXT = "Принял сообщение. Это минимальный ответ от бота."
MENU_COMMAND_TEXT = "меню"
MENU_REPLY_TEXT = "Выберите действие:"
KEYBOARD_BUTTON_1_TEXT = "Помощь"
KEYBOARD_BUTTON_2_TEXT = "Статус"
KEYBOARD_BUTTON_3_TEXT = "Время"
STATUS_REPLY_TEXT = "Все в порядке"
HELP_REPLY_TEXT = "Помощь уже в пути"
VIEW_ORDERS_BUTTON_TEXT = "Посмотреть ордера"
ORDERS_LIST_REPLY_TEXT = "Выберите номер ордера:"
ORDER_MENU_REPLY_TEXT = "Ордер {order_id}. Выберите действие:"
ORDER_CONTEXT_MISSING_TEXT = "Сначала выберите ордер через кнопку 'Посмотреть ордера'."
ORDER_STATUS_BUTTON_TEXT = "Статус ордера"
ORDER_ITEMS_BUTTON_TEXT = "Состав"
ORDER_AMOUNT_BUTTON_TEXT = "Сумма"
BACK_TO_ORDERS_BUTTON_TEXT = "Назад к ордерам"
BACK_TO_MAIN_BUTTON_TEXT = "Назад в главное меню"
DEMO_ORDER_NUMBERS = ("ORD-1001", "ORD-1002", "ORD-1003")


@dataclass(frozen=True)
class Settings:
    bitrix_domain: str
    webhook_user_id: str
    webhook_token: str
    bot_token: str
    bot_id: int | None
    bot_code: str
    bot_name: str
    bot_type: str
    bot_work_position: str
    event_type: str
    event_types: tuple[str, ...]
    polling_timeout: int
    polling_limit: int
    polling_sleep_seconds: float
    notify_on_start: bool
    startup_notify_dialog_id: str
    startup_message: str
    skip_backlog_on_start: bool
    default_reply_text: str
    menu_command_text: str
    menu_reply_text: str
    keyboard_button_1_text: str
    keyboard_button_2_text: str
    keyboard_button_3_text: str
    status_reply_text: str
    help_reply_text: str
    view_orders_button_text: str
    orders_list_reply_text: str
    order_menu_reply_text: str
    order_context_missing_text: str
    order_status_button_text: str
    order_items_button_text: str
    order_amount_button_text: str
    back_to_orders_button_text: str
    back_to_main_button_text: str
    demo_order_numbers: tuple[str, ...]


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def _to_bool(value: str, default: bool) -> bool:
    normalized = value.strip().lower()
    if not normalized:
        return default
    return normalized in {"1", "true", "yes", "y", "on"}


def _parse_event_types(raw_event_types: str, event_type: str) -> tuple[str, ...]:
    if raw_event_types:
        tokens = tuple(token.strip() for token in raw_event_types.split(",") if token.strip())
        if tokens:
            return tokens
        return (event_type,)
    if "," in event_type:
        tokens = tuple(token.strip() for token in event_type.split(",") if token.strip())
        if tokens:
            return tokens
    return ("message", "command")


def load_settings() -> Settings:
    load_dotenv()
    raw_bot_id = os.getenv("BITRIX_BOT_ID", "").strip()
    raw_event_types = os.getenv("BITRIX_EVENT_TYPES", "").strip()
    event_type = os.getenv("BITRIX_EVENT_TYPE", "message").strip() or "message"
    parsed_event_types = _parse_event_types(raw_event_types, event_type)

    return Settings(
        bitrix_domain=_require_env("BITRIX_DOMAIN"),
        webhook_user_id=_require_env("BITRIX_WEBHOOK_USER_ID"),
        webhook_token=_require_env("BITRIX_WEBHOOK_TOKEN"),
        bot_token=_require_env("BITRIX_BOT_TOKEN"),
        bot_id=int(raw_bot_id) if raw_bot_id else None,
        bot_code=os.getenv("BITRIX_BOT_CODE", "support_bot").strip() or "support_bot",
        bot_name=os.getenv("BITRIX_BOT_NAME", "Support Bot").strip() or "Support Bot",
        bot_type=os.getenv("BITRIX_BOT_TYPE", "personal").strip() or "personal",
        bot_work_position=os.getenv("BITRIX_BOT_WORK_POSITION", "AI Assistant").strip()
        or "AI Assistant",
        event_type=event_type,
        event_types=parsed_event_types,
        polling_timeout=int(os.getenv("BITRIX_POLLING_TIMEOUT", "25")),
        polling_limit=int(os.getenv("BITRIX_POLLING_LIMIT", "100")),
        polling_sleep_seconds=float(os.getenv("BITRIX_POLLING_SLEEP_SECONDS", "1.0")),
        notify_on_start=_to_bool(os.getenv("BITRIX_NOTIFY_ON_START", "true"), True),
        startup_notify_dialog_id=os.getenv("BITRIX_STARTUP_NOTIFY_DIALOG_ID", "2823").strip()
        or "2823",
        startup_message=os.getenv(
            "BITRIX_STARTUP_MESSAGE", "Бот запущен и готов к работе"
        ).strip()
        or "Бот запущен и готов к работе",
        skip_backlog_on_start=_to_bool(os.getenv("BITRIX_SKIP_BACKLOG_ON_START", "true"), True),
        default_reply_text=DEFAULT_REPLY_TEXT,
        menu_command_text=MENU_COMMAND_TEXT,
        menu_reply_text=MENU_REPLY_TEXT,
        keyboard_button_1_text=KEYBOARD_BUTTON_1_TEXT,
        keyboard_button_2_text=KEYBOARD_BUTTON_2_TEXT,
        keyboard_button_3_text=KEYBOARD_BUTTON_3_TEXT,
        status_reply_text=STATUS_REPLY_TEXT,
        help_reply_text=HELP_REPLY_TEXT,
        view_orders_button_text=VIEW_ORDERS_BUTTON_TEXT,
        orders_list_reply_text=ORDERS_LIST_REPLY_TEXT,
        order_menu_reply_text=ORDER_MENU_REPLY_TEXT,
        order_context_missing_text=ORDER_CONTEXT_MISSING_TEXT,
        order_status_button_text=ORDER_STATUS_BUTTON_TEXT,
        order_items_button_text=ORDER_ITEMS_BUTTON_TEXT,
        order_amount_button_text=ORDER_AMOUNT_BUTTON_TEXT,
        back_to_orders_button_text=BACK_TO_ORDERS_BUTTON_TEXT,
        back_to_main_button_text=BACK_TO_MAIN_BUTTON_TEXT,
        demo_order_numbers=DEMO_ORDER_NUMBERS,
    )
