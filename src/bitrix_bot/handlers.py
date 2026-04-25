from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Any

from bitrix_bot.client import BitrixClient
from bitrix_bot.config import Settings
from bitrix_bot.keyboard import (
    build_main_menu_keyboard,
    build_order_menu_keyboard,
    build_orders_list_keyboard,
)

LOGGER = logging.getLogger(__name__)
SUPPORTED_EVENT_TYPES = {"ONIMBOTV2MESSAGEADD", "ONIMBOTV2COMMANDADD"}
MODE_MAIN_MENU = "main_menu"
MODE_ORDERS_LIST = "orders_list"
MODE_ORDER_MENU = "order_menu"


@dataclass
class DialogContext:
    mode: str = MODE_MAIN_MENU
    selected_order_id: str | None = None


_DIALOG_CONTEXTS: dict[str, DialogContext] = {}


def _as_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _extract_command_value(data: dict[str, Any], event: dict[str, Any]) -> str:
    message = data.get("message") or data.get("MESSAGE") or {}
    message_params = (
        message.get("params") if isinstance(message, dict) else None
    ) or (message.get("PARAMS") if isinstance(message, dict) else None) or {}
    raw_command = (
        data.get("command")
        or data.get("COMMAND")
        or (message_params.get("COMMAND") if isinstance(message_params, dict) else None)
        or (message_params.get("command") if isinstance(message_params, dict) else None)
        or event.get("command")
        or event.get("COMMAND")
        or ""
    )
    if isinstance(raw_command, dict):
        for key in ("value", "command", "text", "COMMAND", "VALUE"):
            if raw_command.get(key):
                return str(raw_command[key])
        return ""
    return _as_string(raw_command)


def _extract_dialog_id(data: dict[str, Any]) -> str:
    chat = data.get("chat") or data.get("CHAT") or {}
    message = data.get("message") or data.get("MESSAGE") or {}
    dialog = data.get("dialog") or data.get("DIALOG") or {}
    candidates = [
        data.get("dialogId"),
        data.get("DIALOG_ID"),
        chat.get("dialogId") if isinstance(chat, dict) else None,
        chat.get("DIALOG_ID") if isinstance(chat, dict) else None,
        chat.get("id") if isinstance(chat, dict) else None,
        chat.get("ID") if isinstance(chat, dict) else None,
        dialog.get("id") if isinstance(dialog, dict) else None,
        dialog.get("ID") if isinstance(dialog, dict) else None,
        message.get("dialogId") if isinstance(message, dict) else None,
        message.get("DIALOG_ID") if isinstance(message, dict) else None,
    ]
    for value in candidates:
        normalized = _as_string(value).strip()
        if normalized:
            return normalized

    message_chat_id = (
        message.get("chatId") if isinstance(message, dict) else None
    ) or (message.get("CHAT_ID") if isinstance(message, dict) else None)
    message_chat_id_text = _as_string(message_chat_id).strip()
    if message_chat_id_text:
        return f"chat{message_chat_id_text}"
    return ""


def _extract_message_event_data(
    event: dict[str, Any],
) -> tuple[str | None, str | None, str | None]:
    data = event.get("data") or event.get("DATA") or {}
    dialog_id = _extract_dialog_id(data)
    message = data.get("message") or data.get("MESSAGE") or {}
    message_text = (
        (message.get("text") if isinstance(message, dict) else None)
        or (message.get("TEXT") if isinstance(message, dict) else None)
        or data.get("text")
        or data.get("TEXT")
        or ""
    )
    command = _extract_command_value(data, event)
    if not dialog_id:
        return None, None, None
    return dialog_id, _as_string(message_text), _as_string(command)


def build_reply_text(incoming_text: str, fallback_text: str) -> str:
    cleaned = incoming_text.strip()
    if not cleaned:
        return fallback_text
    return f"Ответ на {cleaned}"


def _resolve_action(settings: Settings, incoming_text: str, command: str) -> str:
    normalized_text = incoming_text.strip().lower()
    normalized_command = command.strip().lower()
    if normalized_command == "/меню" or normalized_text in {
        settings.menu_command_text.lower(),
        f"/{settings.menu_command_text.lower()}",
    }:
        return "menu"
    if normalized_text == settings.view_orders_button_text.lower():
        return "view_orders"
    if normalized_text == settings.keyboard_button_2_text.lower():
        return "status"
    if normalized_text == settings.keyboard_button_1_text.lower():
        return "help"
    if normalized_text == settings.keyboard_button_3_text.lower():
        return "time"
    if normalized_text in {order_id.lower() for order_id in settings.demo_order_numbers}:
        return "select_order"
    if normalized_text == settings.order_status_button_text.lower():
        return "order_status"
    if normalized_text == settings.order_items_button_text.lower():
        return "order_items"
    if normalized_text == settings.order_amount_button_text.lower():
        return "order_amount"
    if normalized_text == settings.back_to_orders_button_text.lower():
        return "back_to_orders"
    if normalized_text == settings.back_to_main_button_text.lower():
        return "back_to_main"
    return "echo"


def _main_menu_keyboard(settings: Settings) -> list[dict[str, str]]:
    return build_main_menu_keyboard(
        view_orders_text=settings.view_orders_button_text,
        status_text=settings.keyboard_button_2_text,
        help_text=settings.keyboard_button_1_text,
        time_text=settings.keyboard_button_3_text,
    )


def _orders_list_keyboard(settings: Settings) -> list[dict[str, str]]:
    return build_orders_list_keyboard(
        order_numbers=settings.demo_order_numbers,
        back_to_main_text=settings.back_to_main_button_text,
    )


def _selected_order_message(settings: Settings, order_id: str) -> str:
    return settings.order_menu_reply_text.format(order_id=order_id)


def _order_menu_keyboard(settings: Settings) -> list[dict[str, str]]:
    return build_order_menu_keyboard(
        status_text=settings.order_status_button_text,
        items_text=settings.order_items_button_text,
        amount_text=settings.order_amount_button_text,
        back_to_orders_text=settings.back_to_orders_button_text,
        back_to_main_text=settings.back_to_main_button_text,
    )


def _get_dialog_context(dialog_id: str) -> DialogContext:
    context = _DIALOG_CONTEXTS.get(dialog_id)
    if context is None:
        context = DialogContext()
        _DIALOG_CONTEXTS[dialog_id] = context
    return context


def _resolve_response(
    settings: Settings,
    action: str,
    incoming_text: str,
    context: DialogContext,
) -> tuple[str, list[dict[str, str]] | None]:
    if action == "menu":
        context.mode = MODE_MAIN_MENU
        context.selected_order_id = None
        return settings.menu_reply_text, _main_menu_keyboard(settings)
    if action == "view_orders":
        context.mode = MODE_ORDERS_LIST
        context.selected_order_id = None
        return settings.orders_list_reply_text, _orders_list_keyboard(settings)
    if action == "select_order":
        selected_order = next(
            (order for order in settings.demo_order_numbers if order.lower() == incoming_text.strip().lower()),
            None,
        )
        if selected_order is None:
            return settings.orders_list_reply_text, _orders_list_keyboard(settings)
        context.mode = MODE_ORDER_MENU
        context.selected_order_id = selected_order
        return _selected_order_message(settings, selected_order), _order_menu_keyboard(settings)
    if action == "back_to_orders":
        context.mode = MODE_ORDERS_LIST
        context.selected_order_id = None
        return settings.orders_list_reply_text, _orders_list_keyboard(settings)
    if action == "back_to_main":
        context.mode = MODE_MAIN_MENU
        context.selected_order_id = None
        return settings.menu_reply_text, _main_menu_keyboard(settings)
    if action == "status":
        return settings.status_reply_text, None
    if action == "help":
        return settings.help_reply_text, None
    if action == "time":
        return datetime.now().strftime("%H:%M"), None
    if action in {"order_status", "order_items", "order_amount"}:
        if context.mode != MODE_ORDER_MENU or not context.selected_order_id:
            context.mode = MODE_ORDERS_LIST
            return settings.order_context_missing_text, _orders_list_keyboard(settings)
        order_id = context.selected_order_id
        if action == "order_status":
            return f"Ордер {order_id}: все в порядке (демо).", _order_menu_keyboard(settings)
        if action == "order_items":
            return f"Ордер {order_id}: позиции A, B, C (демо).", _order_menu_keyboard(settings)
        return f"Ордер {order_id}: сумма 12 345 RUB (демо).", _order_menu_keyboard(settings)
    return build_reply_text(incoming_text, settings.default_reply_text), None


def handle_event(client: BitrixClient, settings: Settings, event: dict[str, Any]) -> bool:
    event_type = _as_string(event.get("type") or event.get("TYPE"))
    if event_type and event_type not in SUPPORTED_EVENT_TYPES:
        LOGGER.info("Event skipped: unsupported type=%s", event_type)
        return False

    dialog_id, incoming_text, command = _extract_message_event_data(event)
    if not dialog_id:
        LOGGER.info("Event skipped: no dialog_id type=%s", event_type or "unknown")
        return False

    normalized_text = incoming_text or ""
    action = _resolve_action(settings, normalized_text, command or "")
    context = _get_dialog_context(dialog_id)
    prev_mode = context.mode
    prev_order_id = context.selected_order_id
    reply_text, keyboard = _resolve_response(settings, action, normalized_text, context)

    client.send_message(
        bot_id=settings.bot_id,
        dialog_id=dialog_id,
        message=reply_text,
        keyboard=keyboard,
    )
    LOGGER.info(
        "Event handled: type=%s dialog=%s action=%s mode=%s->%s order=%s->%s text='%s' command='%s'",
        event_type or "unknown",
        dialog_id,
        action,
        prev_mode,
        context.mode,
        prev_order_id or "-",
        context.selected_order_id or "-",
        normalized_text.strip()[:80],
        (command or "").strip()[:80],
    )
    return True
