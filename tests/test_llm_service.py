from unittest.mock import patch
from urllib.error import URLError, HTTPError
from io import BytesIO
import json
import pytest
from app.services.llm_service import OllamaClient, LLMServiceError


@pytest.fixture
def client():
    return OllamaClient('http://127.0.0.1:11434/api/chat', 'qwen3:1.7b')


def test_payload_and_answer(client):
    response = BytesIO(json.dumps({'message': {'content': '  Готово!  '}}).encode())
    with patch('app.services.llm_service.request.urlopen', return_value=response) as urlopen:
        answer = client.analyze('Встретимся завтра', 'tasks')
    assert answer == 'Готово!'
    req = urlopen.call_args.args[0]
    payload = json.loads(req.data)
    assert payload['model'] == 'qwen3:1.7b'
    assert payload['stream'] is False
    assert payload['think'] is False
    assert payload['messages'][1]['role'] == 'user'


@pytest.mark.parametrize('text,mode', [('', 'summary'), ('х', 'invalid')])
def test_invalid_input(client, text, mode):
    with pytest.raises(ValueError):
        client.analyze(text, mode)


def test_too_long(client):
    with pytest.raises(ValueError):
        client.analyze('a' * 8001, 'summary')


def test_ollama_offline(client):
    with patch('app.services.llm_service.request.urlopen', side_effect=URLError('offline')):
        with pytest.raises(LLMServiceError, match='Ollama'):
            client.analyze('текст', 'summary')


def test_empty_llm_response(client):
    with patch('app.services.llm_service.request.urlopen', return_value=BytesIO(b'{"message": {"content":""}}')):
        with pytest.raises(LLMServiceError, match='пустой'):
            client.analyze('текст', 'summary')
