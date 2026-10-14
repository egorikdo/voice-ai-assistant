"""Зависимости бота, передаваемые обработчикам через aiogram DI."""
from dataclasses import dataclass, field
from asyncio import Semaphore
from app.config import Settings
from app.services.storage import SQLiteStore
from app.services.speech_to_text import SpeechService
from app.services.llm_service import OllamaClient


@dataclass
class Services:
    settings: Settings
    storage: SQLiteStore
    speech: SpeechService
    llm: OllamaClient
    # Один одновременный LLM-запрос и одно распознавание на компактном Mac.
    llm_semaphore: Semaphore = field(default_factory=lambda: Semaphore(1))
    speech_semaphore: Semaphore = field(default_factory=lambda: Semaphore(1))


def create_services(settings: Settings) -> Services:
    return Services(
        settings=settings,
        storage=SQLiteStore(settings.db_path),
        speech=SpeechService(settings.model_path),
        llm=OllamaClient(settings.ollama_url, settings.ollama_model, settings.max_llm_chars),
    )
