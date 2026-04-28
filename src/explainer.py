import logging
from openai import OpenAI
from src.recommender import Song

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a friendly music curator. Given a user's music request and a list of "
    "recommended songs with their attributes, write a cohesive 2-3 sentence explanation "
    "of why these songs match the request. Be specific about song qualities. "
    "Do not use bullet points."
)


def explain(user_input: str, recommendations: list) -> str:
    song_lines = []
    for song, score, reasons in recommendations:
        reason_str = ", ".join(reasons) if reasons else "overall match"
        song_lines.append(
            f"- {song.title} by {song.artist} "
            f"(genre: {song.genre}, mood: {song.mood}, energy: {song.energy:.2f}, "
            f"score: {score:.2f}; reasons: {reason_str})"
        )
    songs_context = "\n".join(song_lines)

    user_message = (
        f'User request: "{user_input}"\n\n'
        f"Recommended songs:\n{songs_context}\n\n"
        "Write a 2-3 sentence explanation of why these songs match the request."
    )

    client = OpenAI()
    logger.info("explainer: gpt-4o-mini call, songs=%d", len(recommendations))
    logger.debug("explainer context: %s", user_message)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    return response.choices[0].message.content.strip()
