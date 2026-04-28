import logging
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv(override=False)

if not os.environ.get("OPENAI_API_KEY"):
    raise EnvironmentError(
        "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
    )

from src.recommender import load_songs, recommend_songs
from src.interpreter import interpret
from src.explainer import explain

logger = logging.getLogger(__name__)

_songs = None


def _get_songs():
    global _songs
    if _songs is None:
        _songs = load_songs("data/songs.csv")
    return _songs


@dataclass
class AgentResult:
    recommendations: list = field(default_factory=list)
    explanation: str = ""
    error: str | None = None


def run(user_input: str, k: int = 5) -> AgentResult:
    if not user_input or not user_input.strip():
        return AgentResult(error="Input cannot be empty.")
    if len(user_input) > 500:
        return AgentResult(error="Input must be 500 characters or fewer.")

    try:
        user_prefs = interpret(user_input)
        recs = recommend_songs(user_prefs, _get_songs(), k=k, mode="genre_first", diversity=True)
        if not recs:
            return AgentResult(error="No matching songs found for your request.")
        explanation = explain(user_input, recs)
        return AgentResult(recommendations=recs, explanation=explanation)
    except Exception as exc:
        logger.error("agent.run error: %s", exc)
        return AgentResult(error=str(exc))
