from __future__ import annotations

import json

from bitrix_bot.client import BitrixClient
from bitrix_bot.config import load_settings


def main() -> None:
    settings = load_settings()
    client = BitrixClient(
        bitrix_domain=settings.bitrix_domain,
        webhook_user_id=settings.webhook_user_id,
        webhook_token=settings.webhook_token,
        bot_token=settings.bot_token,
    )

    result = client.register_bot_v2(
        code=settings.bot_code,
        name=settings.bot_name,
        work_position=settings.bot_work_position,
        bot_type=settings.bot_type,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
