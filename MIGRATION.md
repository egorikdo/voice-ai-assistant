# Переход с `vmr_bot.py` на модульную версию — macOS

**Сначала останови бот** через `Control + C` в VS Code.

## 1. Сохрани полностью рабочий проект

В Finder сделай копию старой папки `voice-ai-assistant` (⌘+D), назови её `voice-ai-assistant-backup`. В копии должны остаться `.env`, `data/transcriptions.db` и `vosk-model-small-ru-0.22`. Не загружай эту папку в GitHub.

## 2. Распакуй ZIP

Архив содержит папку `voice-ai-assistant/`. **Скопируй содержимое новой папки внутрь существующей папки проекта**, с заменой одноимённых исходных файлов. Это не должно затронуть `data/transcriptions.db`, `.env` и модель Vosk, которых нет в ZIP.

На Mac удобно сделать через Terminal (подставь реальные пути):

```bash
# Пример: старый проект находится в ~/Downloads/voice-ai-assistant
# ZIP распакован во временную папку ~/Downloads/voice-ai-refactored/voice-ai-assistant
cd ~/Downloads/voice-ai-assistant
# Сначала резервная копия всей папки через Finder!
ditto ~/Downloads/voice-ai-refactored/voice-ai-assistant/ ./
```

Не запускай пример командой с выдуманными путями: сначала проверь, где лежат папки. `ditto` переносит также скрытые `.gitignore` и `.github`; он не удаляет локальную `.env`, базу или модель.

## 3. Сохрани старые данные

Новое приложение по умолчанию использует тот же путь к SQLite: `data/transcriptions.db`. Схема совместима; миграционный тест подтверждает чтение существующих записей. При отсутствии файла SQLite создаст пустую базу.

В корне проекта после копирования старые `storage.py` и `llm_service.py` больше **не используются**. Их можно перенести в резервную копию — новые версии находятся в `app/services/`.

## 4. Обнови настройки

Проверь `.env`: обязательная переменная `TELEGRAM_BOT_TOKEN` остаётся неизменной. Опционально добавь `ADMIN_USER_ID=...` для /restart. Остальное можно оставить по умолчанию (значения в `.env.example`).

## 5. Проверка

```bash
conda activate voice-ai
python -m pip install -r requirements.txt
python -m pip install pytest
python -m pytest -q
python vmr_bot.py
```

В Telegram последовательно проверь:

1. `/start` и `/help`.
2. Голосовое на русском (Vosk распознаёт).
3. `/history` — сохранение новых и прежних записей.
4. `/export` — TXT-файл.
5. `/summary` и `/tasks` — Ollama отвечает.
6. `/clear` — только если готов **удалить свои реальные транскрипции**.

Если возникла проблема — останови приложение и верни папку из резервной копии.
