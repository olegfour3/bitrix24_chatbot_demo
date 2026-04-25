from __future__ import annotations

from collections import deque
import logging
import time
from typing import Any

from bitrix_bot.client import BitrixClient
from bitrix_bot.config import Settings
from bitrix_bot.handlers import handle_event

LOGGER = logging.getLogger(__name__)


def _event_key(event: dict[str, Any], stream_type: str) -> str:
    event_name = str(event.get("type") or event.get("TYPE") or "")
    event_id = event.get("eventId") or event.get("EVENT_ID")
    if event_id:
        if event_name == "ONIMBOTV2MESSAGEADD":
            # Bitrix may return MESSAGEADD in both streams; de-duplicate globally.
            return f"message:{event_id}"
        return f"{stream_type}:{event_id}"
    update_id = event.get("updateId") or event.get("UPDATE_ID")
    if update_id:
        return f"{stream_type}:{update_id}"
    return f"{stream_type}:{hash(str(event))}"


def _warmup_offset(client: BitrixClient, settings: Settings) -> int | None:
    if not settings.skip_backlog_on_start:
        return None

    payload = client.get_events(
        bot_id=settings.bot_id,
        limit=settings.polling_limit,
        timeout=1,
        offset=None,
    )
    result = payload.get("result", {})
    next_offset = result.get("nextOffset")
    if isinstance(next_offset, int):
        return next_offset
    return None


def run_polling_loop(client: BitrixClient, settings: Settings) -> None:
    seen_queue: deque[str] = deque(maxlen=2000)
    seen_set: set[str] = set()
    offset = _warmup_offset(client, settings)

    while True:
        try:
            handled_count = 0
            payload = client.get_events(
                bot_id=settings.bot_id,
                limit=settings.polling_limit,
                timeout=settings.polling_timeout,
                offset=offset,
            )
            result = payload.get("result", {})
            events = result.get("events", [])
            next_offset = result.get("nextOffset")
            if isinstance(next_offset, int):
                offset = next_offset
            if events:
                LOGGER.info(
                    "Polling batch: fetched=%s next_offset=%s",
                    len(events),
                    offset if offset is not None else "-",
                )
            duplicate_count = 0
            for event in events:
                key = _event_key(event, "default")
                if key in seen_set:
                    duplicate_count += 1
                    continue
                if len(seen_queue) == seen_queue.maxlen:
                    dropped = seen_queue.popleft()
                    seen_set.discard(dropped)
                seen_queue.append(key)
                seen_set.add(key)
                if handle_event(client, settings, event):
                    handled_count += 1

            if events:
                LOGGER.info(
                    "Polling batch result: handled=%s duplicates=%s skipped=%s",
                    handled_count,
                    duplicate_count,
                    max(len(events) - handled_count - duplicate_count, 0),
                )
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception("Polling iteration failed: %s", exc)
            time.sleep(max(settings.polling_sleep_seconds, 1.0))
            continue

        time.sleep(settings.polling_sleep_seconds)
