import json
import sys
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch
import pytest
from app.services.speech_to_text import SpeechService


def test_missing_model(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        SpeechService(tmp_path / 'absent').load()


def test_recognizer_mocked(tmp_path, monkeypatch):
    model = tmp_path / 'vosk'
    model.mkdir()
    class FakeRecognizer:
        def __init__(self, model_arg, sample_rate):
            assert sample_rate == 16000
        def SetWords(self, val):
            assert val
        def AcceptWaveform(self, data):
            return True
        def Result(self):
            return json.dumps({'text': 'привет', 'result': [{'conf': 0.8}]})
        def FinalResult(self):
            return json.dumps({'text': 'мир', 'result': [{'conf': 1.0}]})
    monkeypatch.setitem(sys.modules, 'vosk', SimpleNamespace(
        Model=lambda path: object(), KaldiRecognizer=FakeRecognizer
    ))
    with patch('app.services.speech_to_text.convert_to_pcm', return_value=b'audio'):
        service = SpeechService(model)
        service.load()
        result = service.recognize(b'not real audio')
    assert result.text == 'привет мир'
    assert result.language == 'ru'
    assert result.confidence == pytest.approx(0.9)


def test_requires_loaded_model(tmp_path):
    with pytest.raises(RuntimeError, match='не загружена'):
        SpeechService(tmp_path).recognize(b'data')
