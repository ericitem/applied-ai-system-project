from unittest.mock import patch, MagicMock
from src.recommender import Song
from src.explainer import explain


def _make_recommendations():
    song = Song(id=1, title="Pop Hit", artist="Artist A", genre="pop", mood="happy",
                energy=0.8, tempo_bpm=120, valence=0.9, danceability=0.8, acousticness=0.2)
    return [(song, 0.85, ["genre match (+0.27)", "mood match (+0.23)"])]


def _mock_response(content: str):
    mock = MagicMock()
    mock.choices[0].message.content = content
    return mock


@patch("src.explainer.OpenAI")
def test_explain_returns_non_empty_string(mock_openai_cls):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response(
        "These pop tracks match your Friday night vibe perfectly."
    )

    result = explain("upbeat pop for Friday night", _make_recommendations())

    assert isinstance(result, str)
    assert result.strip() != ""


@patch("src.explainer.OpenAI")
def test_explain_passes_song_data_to_prompt(mock_openai_cls):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response("Great match.")

    explain("upbeat pop for Friday night", _make_recommendations())

    call_args = mock_client.chat.completions.create.call_args
    messages = call_args.kwargs["messages"] if call_args.kwargs else call_args[1]["messages"]
    user_message = next(m["content"] for m in messages if m["role"] == "user")

    assert "Pop Hit" in user_message
    assert "Artist A" in user_message
