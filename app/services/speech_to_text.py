"""Локальная русскоязычная ASR на Vosk."""
from dataclasses import dataclass
from pathlib import Path
import json

from app.utils.audio import convert_to_pcm


@dataclass(frozen=True)
class Recognition:
    text: str
    confidence: float
    language: str = 'ru'


class SpeechService:
    def __init__(self, model_path: Path):
        self.model_path = Path(model_path)
        self._model = None

    def load(self) -> None:
        if not self.model_path.is_dir():
            raise FileNotFoundError(
                f'Модель Vosk не найдена: {self.model_path}. '
                'Скачай vosk-model-small-ru-0.22 и распакуй в корень проекта.'
            )
        # Ленивый импорт: тесты хранения и LLM не требуют vosk.
        from vosk import Model
        self._model = Model(str(self.model_path))

    def recognize(self, audio_bytes: bytes) -> Recognition:
        if self._model is None:
            raise RuntimeError('Модель Vosk не загружена')
        from vosk import KaldiRecognizer
        pcm = convert_to_pcm(audio_bytes)
        recognizer = KaldiRecognizer(self._model, 16000)
        recognizer.SetWords(True)
        # Для больших аудио обрабатываем данные по частям.
        segments: list[str] = []
        all_words: list[dict] = []
        for i in range(0, len(pcm), 8000):
            if recognizer.AcceptWaveform(pcm[i:i + 8000]):
                # Vosk при паузе возвращает готовый сегмент. Не теряем его.
                part = json.loads(recognizer.Result())
                segments.append(str(part.get('text', '')).strip())
                all_words.extend(part.get('result', []))
        final = json.loads(recognizer.FinalResult())
        segments.append(str(final.get('text', '')).strip())
        all_words.extend(final.get('result', []))
        confidence = (
            sum(float(item.get('conf', 0)) for item in all_words) / len(all_words)
            if all_words else 0.0
        )
        return Recognition(text=' '.join(x for x in segments if x), confidence=confidence)
