from __future__ import annotations

import json
import time
from typing import Any

import requests


class BitrixApiError(RuntimeError):
    pass


class BitrixClient:
    def __init__(
        self,
        bitrix_domain: str,
        webhook_user_id: str,
        webhook_token: str,
        bot_token: str,
    ) -> None:
        self._bitrix_domain = bitrix_domain
        self._webhook_user_id = webhook_user_id
        self._webhook_token = webhook_token
        self._bot_token = bot_token

    @staticmethod
    def _raise_bitrix_payload_error(method: str, status_code: int, payload: dict[str, Any]) -> None:
        error = str(payload.get("error", "UNKNOWN"))
        error_description = str(payload.get("error_description", ""))
        raise BitrixApiError(
            f"Bitrix method {method} failed "
            f"(http={status_code}, error={error}, error_description={error_description}): "
            f"{json.dumps(payload, ensure_ascii=False)}"
        )

    def call_method(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        attempt = 0
        max_attempts = 3
        backoff_seconds = 1.0

        while True:
            url = (
                f"https://{self._bitrix_domain}/rest/"
                f"{self._webhook_user_id}/{self._webhook_token}/{method}"
            )
            response = requests.post(
                url,
                json=params,
                timeout=30,
            )
            if response.status_code == 429 and attempt < max_attempts - 1:
                time.sleep(backoff_seconds)
                backoff_seconds *= 2
                attempt += 1
                continue

            try:
                payload: dict[str, Any] = response.json()
            except ValueError:
                payload = {}

            if response.status_code >= 400:
                if "error" in payload:
                    self._raise_bitrix_payload_error(method, response.status_code, payload)
                response.raise_for_status()

            if "error" in payload:
                self._raise_bitrix_payload_error(method, response.status_code, payload)
            return payload

    def get_events(
        self,
        bot_id: int,
        limit: int,
        timeout: int,
        offset: int | None = None,
        with_user_events: bool = False,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "botId": bot_id,
            "botToken": self._bot_token,
            "limit": limit,
            "timeout": timeout,
        }
        if offset is not None:
            params["offset"] = offset
        if with_user_events:
            params["withUserEvents"] = True

        return self.call_method(
            "imbot.v2.Event.get",
            params,
        )

    def send_message(
        self,
        bot_id: int,
        dialog_id: str,
        message: str,
        keyboard: list[dict[str, str]] | dict[str, Any] | str | None = None,
    ) -> dict[str, Any]:
        fields: dict[str, Any] = {
            "message": message,
        }
        if keyboard is not None:
            fields["keyboard"] = keyboard

        params: dict[str, Any] = {
            "botId": bot_id,
            "botToken": self._bot_token,
            "dialogId": dialog_id,
            "fields": fields,
        }
        return self.call_method("imbot.v2.Chat.Message.send", params)

    def get_message(self, bot_id: int, message_id: int) -> dict[str, Any]:
        return self.call_method(
            "imbot.v2.Chat.Message.get",
            {
                "botId": bot_id,
                "botToken": self._bot_token,
                "messageId": message_id,
            },
        )

    def upload_file(
        self,
        bot_id: int,
        dialog_id: str,
        file_name: str,
        base64_content: str,
        message: str,
    ) -> dict[str, Any]:
        return self.call_method(
            "imbot.v2.File.upload",
            {
                "botId": bot_id,
                "botToken": self._bot_token,
                "dialogId": dialog_id,
                "fields": {
                    "name": file_name,
                    "content": base64_content,
                    "message": message,
                },
            },
        )

    def register_bot_v2(
        self,
        code: str,
        name: str,
        work_position: str,
        bot_type: str = "personal",
    ) -> dict[str, Any]:
        return self.call_method(
            "imbot.v2.Bot.register",
            {
                "fields": {
                    "code": code,
                    "botToken": self._bot_token,
                    "type": bot_type,
                    "eventMode": "fetch",
                    "properties": {
                        "name": name,
                        "workPosition": work_position,
                    },
                },
            },
        )

    def unregister_bot_v2(self, bot_id: int) -> dict[str, Any]:
        return self.call_method(
            "imbot.v2.Bot.unregister",
            {
                "botId": bot_id,
                "botToken": self._bot_token,
            },
        )

    def register_command_v2(
        self,
        bot_id: int,
        command: str,
        title: dict[str, str],
        params: dict[str, str] | None = None,
        hidden: bool = False,
    ) -> dict[str, Any]:
        fields: dict[str, Any] = {
            "command": command,
            "title": title,
            "hidden": hidden,
        }
        if params:
            fields["params"] = params

        return self.call_method(
            "imbot.v2.Command.register",
            {
                "botId": bot_id,
                "botToken": self._bot_token,
                "fields": fields,
            },
        )

