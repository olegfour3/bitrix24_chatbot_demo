from __future__ import annotations

# imbot.v2: см. "Working with Keyboards" — BUTTONS — плоский список кнопок;
# перенос строки — {TYPE: "NEWLINE"}, а не вложенные массивы [[],[]] как в устаревшем imbot.


def _send_button(
    text: str,
    bg_color: str = "#2FC6F6",
    text_color: str = "#000000",
) -> dict[str, str]:
    return {
        "TEXT": text,
        "ACTION": "SEND",
        "ACTION_VALUE": text,
        "DISPLAY": "LINE",
        "BG_COLOR": bg_color,
        "TEXT_COLOR": text_color,
    }


def build_main_menu_keyboard(
    view_orders_text: str,
    status_text: str,
    help_text: str,
    time_text: str,
) -> list[dict[str, str]]:
    return [
        _send_button(view_orders_text),
        {"TYPE": "NEWLINE"},
        _send_button(status_text),
        _send_button(help_text, bg_color="#29619B", text_color="#FFFFFF"),
        {"TYPE": "NEWLINE"},
        _send_button(time_text, bg_color="#FFDC60"),
    ]


def build_orders_list_keyboard(order_numbers: tuple[str, ...], back_to_main_text: str) -> list[dict[str, str]]:
    buttons: list[dict[str, str]] = []
    for idx, order_number in enumerate(order_numbers):
        buttons.append(_send_button(order_number))
        if (idx + 1) % 2 == 0 and idx + 1 < len(order_numbers):
            buttons.append({"TYPE": "NEWLINE"})
    if order_numbers:
        buttons.append({"TYPE": "NEWLINE"})
    buttons.append(_send_button(back_to_main_text, bg_color="#E0E0E0"))
    return buttons


def build_order_menu_keyboard(
    status_text: str,
    items_text: str,
    amount_text: str,
    back_to_orders_text: str,
    back_to_main_text: str,
) -> list[dict[str, str]]:
    return [
        _send_button(status_text),
        _send_button(items_text, bg_color="#29619B", text_color="#FFFFFF"),
        {"TYPE": "NEWLINE"},
        _send_button(amount_text, bg_color="#FFDC60"),
        {"TYPE": "NEWLINE"},
        _send_button(back_to_orders_text, bg_color="#E0E0E0"),
        _send_button(back_to_main_text, bg_color="#D0D0D0"),
    ]


def build_startup_keyboard(menu_text: str) -> list[dict[str, str]]:
    return [_send_button(menu_text)]
