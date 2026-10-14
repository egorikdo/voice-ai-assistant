"""Конвертация аудио в mono PCM 16kHz (формат KaldiRecognizer)."""
import subprocess


class AudioConversionError(RuntimeError):
    pass


def convert_to_pcm(audio: bytes, timeout: int = 35) -> bytes:
    if not audio:
        raise AudioConversionError('Пустой аудиофайл')
    try:
        result = subprocess.run(
            [
                'ffmpeg', '-hide_banner', '-loglevel', 'error',
                '-i', 'pipe:0', '-ar', '16000', '-ac', '1',
                '-acodec', 'pcm_s16le', '-f', 's16le', 'pipe:1',
            ],
            input=audio, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=timeout, check=False,
        )
    except FileNotFoundError as exc:
        raise AudioConversionError('Не установлен FFmpeg или он отсутствует в PATH') from exc
    except subprocess.TimeoutExpired as exc:
        raise AudioConversionError('Превышено время конвертации аудио') from exc
    if result.returncode != 0 or not result.stdout:
        raise AudioConversionError('FFmpeg не смог обработать голосовое сообщение')
    return result.stdout
