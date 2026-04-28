import json
import logging
from dataclasses import dataclass, field
from openai import OpenAI
from tabulate import tabulate
from src.agent import run, AgentResult

logger = logging.getLogger(__name__)

_JUDGE_SYSTEM = (
    "You are an AI quality evaluator for a music recommendation system. "
    "Given a user query, recommended songs, and an explanation, rate on three dimensions from 1-5:\n"
    "- relevance: do the songs match what the user asked for?\n"
    "- diversity: are the songs varied (different artists/styles)?\n"
    "- explanation_quality: is the explanation clear and specific?\n"
    'Return ONLY a JSON object: {"relevance": int, "diversity": int, "explanation_quality": int}'
)

TEST_CASES = [
    {"query": "upbeat pop songs for a morning workout", "expected_genre": "pop", "expected_mood": "happy"},
    {"query": "something chill and relaxing for studying", "expected_genre": "lofi", "expected_mood": "chill"},
    {"query": "high energy music for a party", "expected_genre": "pop", "expected_mood": "happy"},
    {"query": "feel good dance tracks", "expected_genre": "pop", "expected_mood": "happy"},
    {"query": "intense driving music", "expected_genre": "rock", "expected_mood": "intense"},
]


@dataclass
class EvalReport:
    results: list = field(default_factory=list)
    averages: dict = field(default_factory=dict)


def _judge(query: str, result: AgentResult) -> dict:
    songs_text = "\n".join(
        f"- {s.title} by {s.artist} (genre: {s.genre}, mood: {s.mood})"
        for s, _, _ in result.recommendations
    )
    prompt = (
        f'Query: "{query}"\n\n'
        f"Songs recommended:\n{songs_text}\n\n"
        f"Explanation: {result.explanation}"
    )

    client = OpenAI()
    logger.info("evaluator: judge call, query=%r", query[:40])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _JUDGE_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def run_eval(test_cases: list) -> EvalReport:
    results = []
    for tc in test_cases:
        query = tc["query"]
        agent_result = run(query)
        if agent_result.error:
            results.append({"query": query, "error": agent_result.error,
                            "relevance": 0, "diversity": 0, "explanation_quality": 0})
            continue
        scores = _judge(query, agent_result)
        results.append({"query": query, **scores})

    valid = [r for r in results if "error" not in r]
    averages = {}
    if valid:
        averages = {
            "relevance": sum(r["relevance"] for r in valid) / len(valid),
            "diversity": sum(r["diversity"] for r in valid) / len(valid),
            "explanation_quality": sum(r["explanation_quality"] for r in valid) / len(valid),
        }

    return EvalReport(results=results, averages=averages)


def main():
    logging.basicConfig(level=logging.INFO)
    print("\nRunning VibeMatch evaluation...\n")
    report = run_eval(TEST_CASES)

    rows = [
        [r["query"][:45], r.get("relevance", "ERR"), r.get("diversity", "ERR"),
         r.get("explanation_quality", "ERR")]
        for r in report.results
    ]
    print(tabulate(rows, headers=["Query", "Relevance", "Diversity", "Explanation"], tablefmt="simple"))

    if report.averages:
        print(
            f"\nAverages — "
            f"Relevance: {report.averages['relevance']:.1f}/5  "
            f"Diversity: {report.averages['diversity']:.1f}/5  "
            f"Explanation: {report.averages['explanation_quality']:.1f}/5\n"
        )


if __name__ == "__main__":
    main()
