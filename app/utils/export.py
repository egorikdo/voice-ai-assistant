"""Сериализация транскрипций для отправки пользователю в TXT."""


def export_txt(records) -> bytes:
    lines = [
        'VOICE AI ASSISTANT', 'ИСТОРИЯ РАСПОЗНАВАНИЯ РЕЧИ', '=' * 45,
        f'Количество записей: {len(records)}', 'Время в UTC',
        'Включены последние 1000 записей (если их было больше 1000).', '',
    ]
    for num, record in enumerate(records, 1):
        lines.extend([
            '-' * 45, f'Запись №{num}', f'Дата: {record.created_at}',
            f'Язык: {record.language}', 'Текст:', record.text, '',
        ])
    return '\n'.join(lines).encode('utf-8-sig')
