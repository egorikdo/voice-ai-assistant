from app.services.storage import Transcription
from app.utils.export import export_txt


def test_utf8_and_content():
    records = [Transcription('Привет, мир!', 'ru', '2026-10-14T20:00:00+00:00')]
    content = export_txt(records)
    assert content.startswith(b'\xef\xbb\xbf')
    decoded = content.decode('utf-8-sig')
    assert 'Привет, мир!' in decoded
    assert 'Количество записей: 1' in decoded
