"""Конфигурация: загружаем .env относительно корня репозитория."""
from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    model_path: Path
    db_path: Path
    ollama_url: str
    ollama_model: str
    admin_user_id: int | None
    max_voice_seconds: int = 180
    max_audio_bytes: int = 20 * 1024 * 1024
    max_llm_chars: int = 8000


def load_settings() -> Settings:
    load_dotenv(ROOT / '.env')
    token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
    if not token:
        raise ValueError('Укажи TELEGRAM_BOT_TOKEN в .env (см. .env.example)')

    admin_raw = os.getenv('ADMIN_USER_ID', '').strip()
    if admin_raw and not admin_raw.isdecimal():
        raise ValueError('ADMIN_USER_ID должен быть положительным числом')

    model = Path(os.getenv('VOSK_MODEL_PATH', 'vosk-model-small-ru-0.22'))
    db = Path(os.getenv('DB_PATH', 'data/transcriptions.db'))
    # Относительные пути считаем от корня проекта, независимо от cwd.
    if not model.is_absolute():
        model = ROOT / model
    if not db.is_absolute():
        db = ROOT / db

    return Settings(
        telegram_token=token,
        model_path=model,
        db_path=db,
        ollama_url=os.getenv('OLLAMA_URL', 'http://127.0.0.1:11434/api/chat').strip(),
        ollama_model=os.getenv('OLLAMA_MODEL', 'qwen3:1.7b').strip(),
        admin_user_id=int(admin_raw) if admin_raw else None,
    )
