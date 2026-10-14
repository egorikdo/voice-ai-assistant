from types import SimpleNamespace
from unittest.mock import patch
import subprocess
import pytest
from app.utils.audio import convert_to_pcm, AudioConversionError


def test_audio_converted():
    fake = SimpleNamespace(returncode=0, stdout=b'pcm', stderr=b'')
    with patch('app.utils.audio.subprocess.run', return_value=fake) as run:
        assert convert_to_pcm(b'voice') == b'pcm'
        assert run.call_args.kwargs['timeout'] == 35


@pytest.mark.parametrize('fake', [
    SimpleNamespace(returncode=1, stdout=b'', stderr=b'error'),
    SimpleNamespace(returncode=0, stdout=b'', stderr=b''),
])
def test_ffmpeg_error(fake):
    with patch('app.utils.audio.subprocess.run', return_value=fake):
        with pytest.raises(AudioConversionError):
            convert_to_pcm(b'voice')


def test_ffmpeg_timeout():
    with patch('app.utils.audio.subprocess.run', side_effect=subprocess.TimeoutExpired('ffmpeg', 35)):
        with pytest.raises(AudioConversionError, match='время'):
            convert_to_pcm(b'voice')


def test_empty_audio():
    with pytest.raises(AudioConversionError, match='Пустой'):
        convert_to_pcm(b'')
