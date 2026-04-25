# Minimal Bitrix24 Bot (sync, uv)

Минимально рабочий бот для `Bitrix24 Chat bots v2.0` на Python:

- вручную регистрирует бота через `imbot.v2.Bot.register`,
- получает события через `imbot.v2.Event.get` (polling),
- отвечает эхом в формате `Ответ на {текст}`,
- автоматически регистрирует slash-команду `/меню` при старте,
- демонстрирует контекстный flow по ордерам: `Главное меню -> Посмотреть ордера -> Меню выбранного ордера`,
- использует входящий webhook (`/rest/{user_id}/{token}/...`) + `botToken`,
- работает синхронно (без async).

## Стек

- Python 3.11+
- `uv`
- `requests`
- `python-dotenv`

## Полезное

- Ссылка на документацию к API [https://apidocs.bitrix24.ru/api-reference/chat-bots/chat-bots-v2/index.html](https://apidocs.bitrix24.ru/api-reference/chat-bots/chat-bots-v2/index.html)
- В РФ для создания входящего вебхука неоходимо оформлять отдельную подписку на маркетплейсы. В РБ это бесплатно.

## Быстрый запуск

1. Заполни переменные в `.env` (блоки `BITRIX_*`, смотри секцию ниже).
2. Установи зависимости:

```bash
uv sync
```

1. Заполни регистрационные поля и выполни ручную регистрацию бота:

```bash
uv run bitrix-register-bot
```

1. Возьми `botId` из результата регистрации и заполни `BITRIX_BOT_ID`.
2. Если нужно удалить бота, выполни:

```bash
uv run bitrix-unregister-bot
```

Команда удаления использует `BITRIX_BOT_ID` и `BITRIX_BOT_TOKEN` из `.env`.
2. Запусти polling-бота:

```bash
uv run bitrix-bot
```

## Как получить входящий webhook

1. В Bitrix24 открой `Разработчикам -> Другое -> Входящий вебхук`.
2. Создай вебхук и включи права на модуль чатов/ботов (`imbot`/`im`, если доступны отдельно).
3. Скопируй URL вида:
  `https://<portal>.bitrix24.ru/rest/<user_id>/<webhook_token>/`
4. Из URL заполни в `.env`:
  - `BITRIX_DOMAIN=<portal>.bitrix24.ru`
  - `BITRIX_WEBHOOK_USER_ID=<user_id>`
  - `BITRIX_WEBHOOK_TOKEN=<webhook_token>`
5. `BITRIX_BOT_TOKEN` задай заранее (любой секретный токен), он используется в `imbot.v2` методах.
6. Для внутреннего режима сотрудников в `.env` оставь `BITRIX_BOT_TYPE=personal`.

## Структура

- `src/bitrix_bot/config.py` — загрузка и валидация конфигурации
- `src/bitrix_bot/client.py` — sync REST-клиент Bitrix API
- `src/bitrix_bot/poller.py` — polling-цикл с дедупликацией событий
- `src/bitrix_bot/handlers.py` — обработка входящих message-событий
- `src/bitrix_bot/keyboard.py` — генерация payload клавиатуры
- `scripts/register_bot.py` — ручная регистрация `imbot.v2.Bot.register` (`eventMode=fetch`, `type=personal`)
- `scripts/unregister_bot.py` — ручное удаление `imbot.v2.Bot.unregister`

## Переменные окружения (основные)

- `BITRIX_DOMAIN` — домен портала (например `company.bitrix24.ru`)
- `BITRIX_WEBHOOK_USER_ID` — user id из URL входящего webhook
- `BITRIX_WEBHOOK_TOKEN` — секретный токен из URL входящего webhook
- `BITRIX_BOT_TOKEN` — токен бота для `imbot.v2` вызовов
- `BITRIX_BOT_ID` — ID зарегистрированного бота для runtime

## Что заполнять в `.env`

Обязательно для работы runtime:

- `BITRIX_DOMAIN` — домен портала, без `https://`
- `BITRIX_WEBHOOK_USER_ID` — user id из URL вебхука
- `BITRIX_WEBHOOK_TOKEN` — webhook token из URL
- `BITRIX_BOT_TOKEN` — секрет бота (используется в `imbot.v2` payload)
- `BITRIX_BOT_ID` — ID зарегистрированного бота (получаешь после `uv run bitrix-register-bot`)

Обязательно для регистрации:

- `BITRIX_BOT_CODE`
- `BITRIX_BOT_NAME`
- `BITRIX_BOT_TYPE=personal`
- `BITRIX_BOT_WORK_POSITION`

Опционально (можно оставить по умолчанию):

- `BITRIX_EVENT_TYPES` — список типов событий через запятую, рекомендуемо: `message,command`
- `BITRIX_EVENT_TYPE` — fallback для одного типа (по умолчанию `message`)
- `BITRIX_POLLING_TIMEOUT`
- `BITRIX_POLLING_LIMIT`
- `BITRIX_POLLING_SLEEP_SECONDS`
- `BITRIX_NOTIFY_ON_START` — отправлять сервисное сообщение о старте (`true`/`false`)
- `BITRIX_STARTUP_NOTIFY_DIALOG_ID` — `dialogId` для стартового уведомления
- `BITRIX_STARTUP_MESSAGE` — текст стартового уведомления
- `BITRIX_SKIP_BACKLOG_ON_START` — игнорировать накопленные до запуска события (`true`/`false`)

## Логика ответов

- Тексты ответов и подписи кнопок захардкожены в `src/bitrix_bot/config.py`.
- Бот в fetch-режиме слушает события `message` и `command`.
- `/меню`, `меню`, `Меню`: бот отправляет главное меню с кнопкой `Посмотреть ордера`.
- `Посмотреть ордера`: бот отправляет список тестовых номеров ордеров в виде клавиатуры.
- Выбор номера ордера: бот сохраняет `selected_order_id` в контексте текущего `dialogId` и отправляет меню выбранного ордера.
- В меню ордера доступны действия: `Статус ордера`, `Состав`, `Сумма`, `Назад к ордерам`, `Назад в главное меню`.
- Кнопки `Статус ордера` / `Состав` / `Сумма` обрабатываются только при активном контексте выбранного ордера.
- Если контекст ордера отсутствует, бот возвращает пользователя к выбору ордера.
- Любое другое сообщение: `Ответ на {текст входящего сообщения}`.

## Демо-проверка сценария ордеров

1. Запусти бота:

```bash
uv run bitrix-bot
```

1. Отправь `меню` или `/меню` и проверь, что пришло главное меню.
2. Нажми `Посмотреть ордера` и проверь, что пришла клавиатура с тестовыми ордерами.
3. Нажми один номер ордера и проверь, что пришло меню по выбранному ордеру.
4. Нажми `Статус ордера`, `Состав`, `Сумма` и проверь, что ответы содержат номер выбранного ордера.
5. Нажми `Назад к ордерам` и `Назад в главное меню`, проверь корректные переходы.

## Режим старта

- При запуске бот может отправить служебное сообщение «бот запущен и готов к работе».
- Чтобы не реагировать на старые события из очереди, включен warm-up по `nextOffset` (`BITRIX_SKIP_BACKLOG_ON_START=true`).
- После warm-up обрабатываются только новые события.

## Соответствие v2 payload

- `imbot.v2.Bot.register`: `fields{code,botToken,type,eventMode,properties}`
- `imbot.v2.Bot.unregister`: `botId`, `botToken`
- `imbot.v2.Event.get`: `botId`, `botToken`, `limit`, `offset`, `timeout`
- `imbot.v2.Chat.Message.send`: `botId`, `botToken`, `dialogId`, `fields{message,keyboard}`
- `imbot.v2.Chat.Message.get`: `botId`, `botToken`, `messageId`
- `imbot.v2.File.upload`: `botId`, `botToken`, `dialogId`, `fields{name,content,message}`

Slash-команда `/меню` регистрируется автоматически на старте (`imbot.v2.Command.register`).

## Примечания по MVP

- Реализован sync polling без async-кода.
- На `429` применяется экспоненциальный backoff.
- Формат входящих событий у Bitrix может отличаться по полям/регистру, поэтому в обработчике есть безопасные fallback-ключи.
- Бот регистрируется в `type=personal`, то есть предназначен для внутреннего использования сотрудниками портала.

## Диагностика несовместимости и fallback

Если в логах появляются ошибки `ACCESS_DENIED`, `WRONG_AUTH_TYPE`, `insufficient_scope` или похожие:

- это признак, что текущая комбинация `incoming-only + imbot.v2.*` не поддержана на портале;
- минимальный fallback: перейти на `imbot.*` методы и добавить `CLIENT_ID` (application context), сохранив остальную логику обработчиков.

## Ошибки команды удаления

Типовые ошибки `imbot.v2.Bot.unregister`:

- `BOT_TOKEN_NOT_SPECIFIED` — не передан `botToken`
- `BOT_ID_REQUIRED` — не передан `botId`
- `BOT_NOT_FOUND` — бот не найден
- `BOT_OWNERSHIP_ERROR` — бот зарегистрирован другим приложением

