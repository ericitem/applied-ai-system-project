from unittest.mock import patch


def _mock_prefs():
    return {
        "genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False,
        "valence": 0.5, "danceability": 0.5, "target_popularity": 0.5,
        "preferred_decade": 2010, "prefers_instrumental": False,
        "target_loudness": 0.5, "target_speechiness": 0.5,
    }


@patch("src.agent.explain")
@patch("src.agent.interpret")
def test_run_happy_path_returns_result_with_recommendations_and_explanation(
    mock_interpret, mock_explain
):
    mock_interpret.return_value = _mock_prefs()
    mock_explain.return_value = "These songs match your vibe."

    from src.agent import run
    result = run("upbeat pop for a Friday night")

    assert result.error is None
    assert len(result.recommendations) > 0
    assert result.explanation == "These songs match your vibe."


def test_run_empty_string_returns_error_without_api_call():
    from src.agent import run
    result = run("")
    assert result.error is not None
    assert "empty" in result.error.lower()


def test_run_whitespace_only_returns_error():
    from src.agent import run
    result = run("   ")
    assert result.error is not None


def test_run_over_500_chars_returns_error_without_api_call():
    from src.agent import run
    result = run("a" * 501)
    assert result.error is not None
    assert "500" in result.error


@patch("src.agent.interpret")
def test_run_api_exception_returns_error_result_never_raises(mock_interpret):
    mock_interpret.side_effect = Exception("API failure")

    from src.agent import run
    result = run("some valid music request")

    assert result.error is not None
    assert "API failure" in result.error
