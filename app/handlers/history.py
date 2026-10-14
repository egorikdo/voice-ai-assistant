"""Чтение, экспорт и удаление персональной истории."""
from datetime import datetime, timezone

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, Message

from app.container import Services
from app.utils.messages import reply_long
from app.utils.export import export_txt

router = Router(name='history')


def private_user_id(message: Message) -> int | None:
    if message.chat.type != 'private' or message.from_user is None:
        return None
    return message.from_user.id



@router.message(Command('history'))
async def history_command(message: Message, services: Services) -> None:
    user_id = private_user_id(message)
    if user_id is None:
        await message.answer('🔒 История доступна только в личном чате.')
        return
    records = services.storage.recent(user_id, 10)
    if not records:
        await message.answer('📭 История пуста. Отправь голосовое сообщение.')
        return
    lines = ['📚 Последние 10 транскрипций:']
    for num, item in enumerate(records, 1):
        preview = item.text[:220] + ('…' if len(item.text) > 220 else '')
        lines.append(f'{num}. [{item.created_at[:16].replace("T", " ")} UTC] '
                     f'({item.language})\n{preview}')
    await reply_long(message, '\n\n'.join(lines))


@router.message(Command('clear'))
async def clear_command(message: Message, services: Services) -> None:
    user_id = private_user_id(message)
    if user_id is None:
        await message.answer('🔒 Очистка доступна только в личном чате.')
        return
    count = services.storage.clear(user_id)
    await message.answer(f'🗑 Удалено записей: {count}.')


@router.message(Command('export'))
async def export_command(message: Message, services: Services) -> None:
    user_id = private_user_id(message)
    if user_id is None:
        await message.answer('🔒 Экспорт доступен только в личном чате.')
        return
    records = services.storage.recent(user_id, 1000, chronological=True)
    if not records:
        await message.answer('📭 История пуста. Сначала отправь голосовое.')
        return
    content = export_txt(records)
    stamp = datetime.now(timezone.utc).strftime('%Y-%m-%d_%H-%M')
    document = BufferedInputFile(content, filename=f'transcriptions_{stamp}.txt')
    await message.answer_document(document, caption=f'📄 Экспортировано записей: {len(records)}')
