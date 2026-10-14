from pathlib import Path
from app.config import load_settings, ROOT


def test_defaults_and_relative_paths(monkeypatch):
    monkeypatch.setenv('TELEGRAM_BOT_TOKEN', 'fake:token-for-test')
    monkeypatch.delenv('ADMIN_USER_ID', raising=False)
    monkeypatch.setenv('DB_PATH', 'data/transcriptions.db')
    monkeypatch.setenv('VOSK_MODEL_PATH', 'vosk-model-small-ru-0.22')
    config = load_settings()
    assert config.db_path == ROOT / 'data/transcriptions.db'
    assert config.model_path == ROOT / 'vosk-model-small-ru-0.22'
    assert config.admin_user_id is None
