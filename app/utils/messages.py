"""Безопасная отправка длинного plain text в Telegram."""
from aiogram.types import Message

CHUNK_SIZE = 3900


async def reply_long(message: Message, content: str) -> None:
    for start in range(0, len(content), CHUNK_SIZE):
        await message.answer(content[start:start + CHUNK_SIZE])
