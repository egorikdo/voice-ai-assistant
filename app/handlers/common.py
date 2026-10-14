"""Общие команды и справка."""
import asyncio
import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.container import Services

router = Router(name='common')
logger = logging.getLogger(__name__)

WELCOME = (
    '👋 Привет! Я Voice AI Assistant.\n\n'
    'Отправь голосовое сообщение на русском — распознаю его локально через Vosk.\n'
    'Затем попробуй /summary или /tasks для AI-анализа последней записи.\n\n'
    'Все команды: /help'
)
HELP = (
    '📚 Команды Voice AI Assistant\n\n'
    '/start — приветствие\n'
    '/help — инструкция\n'
    '/languages — языки распознавания\n'
    '/history — 10 последних транскрипций\n'
    '/export — выгрузка до 1000 транскрипций в TXT\n'
    '/clear — удалить всю свою историю\n'
    '/summary — пересказ последней транскрипции (Ollama)\n'
    '/tasks — задачи из последней транскрипции (Ollama)\n'
    '/about — технологии и ограничения\n'
    '/changelog — список изменений\n'
    '/restart — перезагрузка модели (только администратор)\n\n'
    '🔐 Бот работает только в личном чате. История хранится локально на машине '
    'с запущенным ботом. Сервис Ollama запускается локально.'
)


@router.message(Command('start'))
async def start_command(message: Message) -> None:
    await message.answer(WELCOME)


@router.message(Command('help'))
async def help_command(message: Message) -> None:
    await message.answer(HELP)


@router.message(Command('languages'))
async def languages_command(message: Message) -> None:
    await message.answer('🌐 Язык распознавания: 🇷🇺 Русский (Vosk)')


@router.message(Command('about'))
async def about_command(message: Message) -> None:
    await message.answer(
        'ℹ️ Voice AI Assistant — переработанный open-source проект с отдельными '
        'компонентами Speech-to-Text, LLM и SQLite.\n\n'
        'Стек: Python, aiogram 3, Vosk, FFmpeg, SQLite, Ollama/Qwen3.\n'
        'Vosk и LLM работают на машине, где запущен бот; Telegram передаёт '
        'голосовые сообщения до получения ботом.\n'
        'ИИ может ошибаться — сверяй важные выводы с оригинальной записью.'
    )


@router.message(Command('changelog'))
async def changelog_command(message: Message) -> None:
    await message.answer(
        '📝 Изменения\n'
        '• Распознавание русской речи Vosk.\n'
        '• История SQLite, команды /history, /clear и /export.\n'
        '• /summary и /tasks через локальную Ollama.\n'
        '• Модульная архитектура, проверки файлов и тесты.'
    )


@router.message(Command('restart'))
async def restart_command(message: Message, services: Services) -> None:
    admin_id = services.settings.admin_user_id
    if message.from_user is None or admin_id is None or message.from_user.id != admin_id:
        await message.answer('🔒 /restart доступна только администратору (ADMIN_USER_ID в .env).')
        return
    async with services.speech_semaphore:
        try:
            await asyncio.to_thread(services.speech.load)
        except Exception:
            logger.exception('Не удалось перезапустить Vosk')
            await message.answer('❌ Не удалось перезагрузить модель. Проверь журнал.')
            return
    await message.answer('🔄 Модель Vosk успешно перезагружена.')


@router.message(F.text & ~F.text.startswith('/'))
async def other_text(message: Message) -> None:
    await message.answer('🎙 Отправь голосовое сообщение. Список команд: /help')
