from __future__ import annotations

import logging

from bitrix_bot.client import BitrixApiError, BitrixClient
from bitrix_bot.config import load_settings
from bitrix_bot.keyboard import build_startup_keyboard
from bitrix_bot.poller import run_polling_loop


def _register_menu_command(client: BitrixClient, bot_id: int, logger: logging.Logger) -> None:
    try:
        client.register_command_v2(
            bot_id=bot_id,
            command="меню",
            title={"ru": "Меню"},
            params={"ru": "открыть меню"},
        )
    except BitrixApiError as exc:
        error_text = str(exc).lower()
        if "command_name_invalid" in error_text:
            # Fallback: some portals allow only latin command names.
            client.register_command_v2(
                bot_id=bot_id,
                command="menu",
                title={"ru": "Меню", "en": "Menu"},
                params={"ru": "открыть меню", "en": "open menu"},
            )
            logger.warning("Команда 'меню' недоступна, зарегистрирована fallback-команда 'menu'")
            return
        if "already" not in error_text and "exists" not in error_text:
            raise
        logger.info("Slash-команда /меню уже зарегистрирована")


def main() -> None:
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    settings = load_settings()
    if settings.bot_id is None:
        raise ValueError("Missing required environment variable for runtime: BITRIX_BOT_ID")
    client = BitrixClient(
        bitrix_domain=settings.bitrix_domain,
        webhook_user_id=settings.webhook_user_id,
        webhook_token=settings.webhook_token,
        bot_token=settings.bot_token,
    )
    _register_menu_command(client, settings.bot_id, logger)
    if settings.notify_on_start:
        client.send_message(
            bot_id=settings.bot_id,
            dialog_id=settings.startup_notify_dialog_id,
            message=settings.startup_message,
            keyboard=build_startup_keyboard(settings.menu_command_text.capitalize()),
        )
    run_polling_loop(client, settings)


if __name__ == "__main__":
    main()
