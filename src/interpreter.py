import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

_DEFAULTS = {
    "genre": "pop",
    "mood": "happy",
    "energy": 0.5,
    "likes_acoustic": False,
    "valence": 0.5,
    "danceability": 0.5,
    "target_popularity": 0.5,
    "preferred_decade": 2010,
    "prefers_instrumental": False,
    "target_loudness": 0.5,
    "target_speechiness": 0.5,
}

_SYSTEM_PROMPT = (
    "You are a music preference parser. Given a natural language request, "
    "extract music preferences and return ONLY a JSON object with these fields:\n"
    '- genre (string): e.g. "pop", "rock", "lofi", "hip-hop", "jazz", "electronic"\n'
    '- mood (string): e.g. "happy", "chill", "intense", "sad", "romantic"\n'
    "- energy (float 0-1): how energetic the music should be\n"
    "- likes_acoustic (bool): true if user prefers acoustic sound\n"
    "- valence (float 0-1): positivity level of the music\n"
    "- danceability (float 0-1): how danceable the music should be\n"
    "Return ONLY valid JSON. No explanation, no markdown."
)


def interpret(user_input: str) -> dict:
    client = OpenAI()
    logger.info("interpreter: gpt-4o-mini call, input_len=%d", len(user_input))
    logger.debug("interpreter input: %s", user_input)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"interpreter: invalid JSON from LLM: {exc!r}\nRaw: {raw}") from exc

    return {**_DEFAULTS, **parsed}
