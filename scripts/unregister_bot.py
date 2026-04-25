from __future__ import annotations

import json

from bitrix_bot.client import BitrixClient
from bitrix_bot.config import load_settings


def main() -> None:
    settings = load_settings()
    if settings.bot_id is None:
        raise ValueError("Missing required environment variable for unregister: BITRIX_BOT_ID")

    client = BitrixClient(
        bitrix_domain=settings.bitrix_domain,
        webhook_user_id=settings.webhook_user_id,
        webhook_token=settings.webhook_token,
        bot_token=settings.bot_token,
    )
    result = client.unregister_bot_v2(bot_id=settings.bot_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
