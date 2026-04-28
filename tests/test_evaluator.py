from unittest.mock import patch, MagicMock
from src.recommender import Song
from src.agent import AgentResult
from src.evaluator import run_eval, EvalReport


def _mock_agent_result():
    song = Song(id=1, title="Pop Hit", artist="Artist A", genre="pop", mood="happy",
                energy=0.8, tempo_bpm=120, valence=0.9, danceability=0.8, acousticness=0.2)
    return AgentResult(
        recommendations=[(song, 0.85, ["genre match"])],
        explanation="Great pop songs for you.",
    )


def _mock_judge_response(scores: dict):
    import json
    mock = MagicMock()
    mock.choices[0].message.content = json.dumps(scores)
    return mock


@patch("src.evaluator.OpenAI")
@patch("src.evaluator.run")
def test_run_eval_returns_eval_report(mock_run, mock_openai_cls):
    mock_run.return_value = _mock_agent_result()
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_judge_response(
        {"relevance": 4, "diversity": 3, "explanation_quality": 5}
    )

    report = run_eval([{"query": "happy pop songs", "expected_genre": "pop", "expected_mood": "happy"}])

    assert isinstance(report, EvalReport)
    assert len(report.results) == 1
    assert "relevance" in report.results[0]
    assert "diversity" in report.results[0]
    assert "explanation_quality" in report.results[0]


@patch("src.evaluator.OpenAI")
@patch("src.evaluator.run")
def test_run_eval_scores_are_in_1_to_5_range(mock_run, mock_openai_cls):
    mock_run.return_value = _mock_agent_result()
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_judge_response(
        {"relevance": 5, "diversity": 4, "explanation_quality": 3}
    )

    report = run_eval([{"query": "chill music", "expected_genre": "lofi", "expected_mood": "chill"}])

    for result in report.results:
        if "error" not in result:
            assert 1 <= result["relevance"] <= 5
            assert 1 <= result["diversity"] <= 5
            assert 1 <= result["explanation_quality"] <= 5


@patch("src.evaluator.OpenAI")
@patch("src.evaluator.run")
def test_run_eval_averages_are_computed(mock_run, mock_openai_cls):
    mock_run.return_value = _mock_agent_result()
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_judge_response(
        {"relevance": 4, "diversity": 4, "explanation_quality": 4}
    )

    test_cases = [
        {"query": "pop songs", "expected_genre": "pop", "expected_mood": "happy"},
        {"query": "chill music", "expected_genre": "lofi", "expected_mood": "chill"},
    ]
    report = run_eval(test_cases)

    assert "relevance" in report.averages
    assert "diversity" in report.averages
    assert "explanation_quality" in report.averages
    assert report.averages["relevance"] == 4.0
