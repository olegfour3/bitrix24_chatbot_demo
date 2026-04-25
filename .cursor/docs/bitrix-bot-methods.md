# Bitrix24 Chat Bot API: методы и возможности

Короткий справочник по методам для чат-ботов в Bitrix24 (упор на `imbot.v2.*`).

## Регистрация и удаление бота

- `imbot.v2.Bot.register`  
  Регистрирует нового бота. Возвращает данные бота и пользователя-бота.
- `imbot.v2.Bot.unregister`  
  Удаляет зарегистрированного бота (по `botId` + `botToken`).

## Команды бота

- `imbot.v2.Command.register`  
  Регистрирует slash-команду (например, `/меню`) для бота.
- `imbot.v2.Command.unregister`  
  Удаляет ранее зарегистрированную команду.
- `imbot.v2.Command.list`  
  Возвращает список команд бота.

## Получение событий

- `imbot.v2.Event.get`  
  Забирает события бота в fetch/polling режиме.  
  Ключевые параметры: `botId`, `botToken`, `limit`, `offset`, `timeout`.

Типовые события:
- `ONIMBOTV2MESSAGEADD` — входящее сообщение.
- `ONIMBOTV2COMMANDADD` — вызов команды.

## Сообщения и чат

- `imbot.v2.Chat.Message.send`  
  Отправляет сообщение в диалог/чат от имени бота (`dialogId`, `fields.message`, `fields.keyboard`).
- `imbot.v2.Chat.Message.update`  
  Обновляет ранее отправленное сообщение бота.
- `imbot.v2.Chat.Message.delete`  
  Удаляет сообщение бота.
- `imbot.v2.Chat.Message.get`  
  Возвращает информацию о сообщении по `messageId`.

## Файлы

- `imbot.v2.File.upload`  
  Загружает файл в чат/диалог от имени бота (можно с текстом сообщения).

## Что умеет бот через эти методы (минимум)

- Регистрироваться/удаляться вручную.
- Регистрировать slash-команды и обрабатывать их.
- Работать через polling (`Event.get`) без async.
- Отправлять текстовые ответы и клавиатуры.
- Держать диалоговые сценарии (через `dialogId` и внутренний state).

## Минимальный набор для рабочего MVP

1. `imbot.v2.Bot.register`
2. `imbot.v2.Event.get`
3. `imbot.v2.Chat.Message.send`
4. `imbot.v2.Command.register` (если нужны slash-команды)
5. `imbot.v2.Bot.unregister` (для controlled cleanup)

## Важно по практике

- Для всех `imbot.v2.*` вызовов обычно нужны `botId` и `botToken`.
- Клавиатуры отправляются через `fields.keyboard` в `imbot.v2.Chat.Message.send`.
- Для стабильной работы в polling режиме используй `offset`/`nextOffset`.
- Проверяй актуальные параметры и ограничения в официальной документации:
  - https://apidocs.bitrix24.ru/api-reference/chat-bots/chat-bots-v2/index.html
