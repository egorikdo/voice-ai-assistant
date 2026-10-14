"""SQLite-хранилище. Схема совместима с прежней data/transcriptions.db."""
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sqlite3


@dataclass(frozen=True)
class Transcription:
    text: str
    language: str
    created_at: str


class SQLiteStore:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)

    def connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(self.db_path, timeout=15)

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS transcriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    language TEXT NOT NULL,
                    confidence REAL,
                    created_at TEXT NOT NULL
                )
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_transcriptions_user_id
                ON transcriptions (user_id, id)
            ''')

    def save(self, user_id: int, text: str, language: str, confidence: float) -> None:
        if not text.strip():
            return
        with self.connect() as conn:
            conn.execute('''
                INSERT INTO transcriptions
                    (user_id, text, language, confidence, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, text, language, confidence,
                  datetime.now(timezone.utc).isoformat()))

    def recent(self, user_id: int, limit: int = 10, chronological: bool = False) -> list[Transcription]:
        limit = max(1, min(int(limit), 1000))
        with self.connect() as conn:
            rows = conn.execute('''
                SELECT text, language, created_at
                FROM transcriptions
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
            ''', (user_id, limit)).fetchall()
        if chronological:
            rows.reverse()
        return [Transcription(*row) for row in rows]

    def clear(self, user_id: int) -> int:
        with self.connect() as conn:
            cursor = conn.execute(
                'DELETE FROM transcriptions WHERE user_id = ?', (user_id,)
            )
            return cursor.rowcount
