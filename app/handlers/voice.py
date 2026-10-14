"""Асинхронная загрузка и ограниченная по ресурсам обработка голосовых."""
import asyncio
import io
import logging

from aiogram import Bot, F, Router
from aiogram.types import Message

from app.container import Services
from app.utils.audio import AudioConversionError
from app.utils.messages import reply_long

router = Router(name='voice')
logger = logging.getLogger(__name__)


@router.message(F.voice)
async def voice_command(message: Message, bot: Bot, services: Services) -> None:
    if message.chat.type != 'private' or message.from_user is None:
        await message.answer('🔒 Для защиты истории отправь голосовое в личный чат с ботом.')
        return
    voice = message.voice
    if voice is None:
        return
    if voice.duration > services.settings.max_voice_seconds:
        await message.answer(
            f'⚠️ Максимальная длительность: {services.settings.max_voice_seconds} секунд.'
        )
        return
    if voice.file_size and voice.file_size > services.settings.max_audio_bytes:
        await message.answer('⚠️ Голосовое слишком большое для текущего режима.')
        return

    status = await message.answer('🎧 Распознаю русскую речь…')
    try:
        stream = io.BytesIO()
        await bot.download(voice, destination=stream)
        audio = stream.getvalue()
        if len(audio) > services.settings.max_audio_bytes:
            await status.edit_text('⚠️ Файл превышает ограничение размера.')
            return
        async with services.speech_semaphore:
            # FFmpeg/Vosk синхронные: выносим работу в поток.
            result = await asyncio.to_thread(services.speech.recognize, audio)
    except AudioConversionError as exc:
        await status.edit_text(f'❌ Не удалось обработать аудио: {exc}')
        return
    except Exception:
        logger.exception('Ошибка обработки голосового сообщения')
        await status.edit_text('❌ Ошибка обработки голосового. Проверь журнал.')
        return

    if not result.text:
        await status.edit_text('🔇 Речь не обнаружена. Попробуй более чёткую запись.')
        return

    services.storage.save(
        message.from_user.id, result.text, result.language, result.confidence
    )
    text = '🔎 Распознано (ru):\n\n' + result.text
    await status.edit_text(text[:3900])
    for start in range(3900, len(text), 3900):
        await message.answer(text[start:start + 3900])
