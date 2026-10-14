"""Операции Ollama над последней расшифровкой пользователя."""
import asyncio
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.container import Services
from app.services.llm_service import LLMServiceError

router = Router(name='ai')
logger = logging.getLogger(__name__)


async def run_analysis(message: Message, services: Services, mode: str) -> None:
    if message.chat.type != 'private' or message.from_user is None:
        await message.answer('🔒 AI-анализ доступен только в личном чате.')
        return

    records = services.storage.recent(message.from_user.id, 1)
    if not records:
        await message.answer('📭 Сначала отправь голосовое сообщение.')
        return
    status = await message.answer('🧠 Анализирую последнюю транскрипцию…')
    async with services.llm_semaphore:
        try:
            result = await asyncio.to_thread(services.llm.analyze, records[0].text, mode)
        except (ValueError, LLMServiceError) as exc:
            await status.edit_text(f'❌ Анализ не выполнен: {exc}')
            return
        except Exception:
            logger.exception('Непредвиденная ошибка при анализе транскрипции')
            await status.edit_text('❌ Ошибка LLM. Проверь журналы приложения.')
            return

    title = '🧠 Краткое содержание' if mode == 'summary' else '✅ Список задач'
    full_text = title + '\n\n' + result
    await status.edit_text(full_text[:3900])
    for start in range(3900, len(full_text), 3900):
        await message.answer(full_text[start:start + 3900])


@router.message(Command('summary'))
async def summary_command(message: Message, services: Services) -> None:
    await run_analysis(message, services, 'summary')


@router.message(Command('tasks'))
async def tasks_command(message: Message, services: Services) -> None:
    await run_analysis(message, services, 'tasks')
