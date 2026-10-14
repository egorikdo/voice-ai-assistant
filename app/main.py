"""Точка входа: python -m app.main."""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from app.config import load_settings
from app.container import create_services
from app.handlers import ai, common, history, voice

logger = logging.getLogger(__name__)


def build_dispatcher():
    dp = Dispatcher()
    # Обработчик обычного текста — последним (в common).
    dp.include_router(history.router)
    dp.include_router(ai.router)
    dp.include_router(voice.router)
    dp.include_router(common.router)
    return dp


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    settings = load_settings()
    services = create_services(settings)
    services.storage.initialize()
    logger.info('Загружаю Vosk-модель…')
    await asyncio.to_thread(services.speech.load)
    logger.info('Vosk готова. Запускаю Telegram-бота.')
    async with Bot(token=settings.telegram_token) as bot:
        dispatcher = build_dispatcher()
        # Стандартный механизм передачи зависимостей в aiogram 3.
        await dispatcher.start_polling(bot, services=services)


if __name__ == '__main__':
    asyncio.run(main())
