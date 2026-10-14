import sqlite3
from pathlib import Path
from app.services.storage import SQLiteStore


def test_isolation_and_chronological_export(tmp_path: Path):
    store = SQLiteStore(tmp_path / 'data' / 'transcriptions.db')
    store.initialize()
    store.save(10, 'первое сообщение', 'ru', 0.9)
    store.save(20, 'другое сообщение', 'ru', 0.8)
    store.save(10, 'второе сообщение', 'ru', 0.7)

    assert [r.text for r in store.recent(10)] == ['второе сообщение', 'первое сообщение']
    assert [r.text for r in store.recent(10, chronological=True)] == [
        'первое сообщение', 'второе сообщение'
    ]
    assert [r.text for r in store.recent(20)] == ['другое сообщение']
    assert store.clear(10) == 2
    assert store.recent(10) == []
    assert len(store.recent(20)) == 1


def test_empty_text_is_not_saved(tmp_path):
    store = SQLiteStore(tmp_path / 'x.db')
    store.initialize()
    store.save(1, '   ', 'ru', 0)
    assert store.recent(1) == []


def test_limit_is_bounded(tmp_path):
    store = SQLiteStore(tmp_path / 'x.db')
    store.initialize()
    for i in range(5):
        store.save(1, str(i), 'ru', 1)
    assert len(store.recent(1, limit=2)) == 2
    assert len(store.recent(1, limit=99999)) == 5


def test_migration_preserves_original_schema_and_rows(tmp_path):
    p = tmp_path / 'data' / 'transcriptions.db'
    p.parent.mkdir()
    with sqlite3.connect(p) as db:
        db.execute('''CREATE TABLE transcriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            language TEXT NOT NULL,
            confidence REAL,
            created_at TEXT NOT NULL)''')
        db.execute('''INSERT INTO transcriptions (user_id,text,language,confidence,created_at)
                      VALUES (42,'старый текст','ru',0.8,'2026-10-14T12:00:00+00:00')''')
    store = SQLiteStore(p)
    store.initialize()
    assert store.recent(42)[0].text == 'старый текст'
    store.save(42, 'новый текст', 'ru', 0.9)
    assert len(store.recent(42)) == 2
