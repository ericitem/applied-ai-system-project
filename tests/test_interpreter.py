import json
from unittest.mock import patch, MagicMock
import pytest
from src.interpreter import interpret, _DEFAULTS


def _mock_response(content: str):
    mock = MagicMock()
    mock.choices[0].message.content = content
    return mock


@patch("src.interpreter.OpenAI")
def test_interpret_returns_dict_with_all_expected_keys(mock_openai_cls):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response(
        json.dumps({"genre": "pop", "mood": "happy", "energy": 0.9,
                    "likes_acoustic": False, "valence": 0.8, "danceability": 0.85})
    )

    result = interpret("upbeat pop for a Friday night")

    assert isinstance(result, dict)
    for key in _DEFAULTS:
        assert key in result, f"Missing key: {key}"


@patch("src.interpreter.OpenAI")
def test_interpret_fills_missing_fields_with_defaults(mock_openai_cls):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response(
        json.dumps({"genre": "rock", "mood": "intense"})
    )

    result = interpret("heavy rock music")

    assert result["genre"] == "rock"
    assert result["mood"] == "intense"
    assert result["energy"] == _DEFAULTS["energy"]
    assert result["valence"] == _DEFAULTS["valence"]
    assert result["danceability"] == _DEFAULTS["danceability"]


@patch("src.interpreter.OpenAI")
def test_interpret_raises_value_error_on_malformed_json(mock_openai_cls):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response("not valid json {{{")

    with pytest.raises(ValueError, match="invalid JSON"):
        interpret("anything")
