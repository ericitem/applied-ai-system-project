import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: float = 50.0
    release_decade: int = 2010
    instrumentalness: float = 0.5
    loudness: float = 0.5
    speechiness: float = 0.5

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_valence: float = 0.5
    target_danceability: float = 0.5
    target_popularity: float = 0.5
    preferred_decade: int = 2010
    prefers_instrumental: bool = False
    target_loudness: float = 0.5
    target_speechiness: float = 0.5

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, song: Song, user: UserProfile) -> float:
        """Compute a weighted compatibility score between a song and a user profile.

        Weights (sum to 1.0):
          genre match      0.30  — strongest categorical signal
          mood match       0.25  — context the user wants right now
          energy sim       0.20  — continuous proximity to target
          acoustic fit     0.10  — electronic vs acoustic preference
          valence sim      0.10  — upbeat vs melancholic preference
          danceability sim 0.05  — secondary rhythmic preference
        """
        genre_match = 1.0 if song.genre == user.favorite_genre else 0.0
        mood_match = 1.0 if song.mood == user.favorite_mood else 0.0
        energy_sim = 1.0 - abs(song.energy - user.target_energy)
        acoustic_fit = song.acousticness if user.likes_acoustic else 1.0 - song.acousticness
        valence_sim = 1.0 - abs(song.valence - user.target_valence)
        dance_sim = 1.0 - abs(song.danceability - user.target_danceability)
        return (
            0.30 * genre_match
            + 0.25 * mood_match
            + 0.20 * energy_sim
            + 0.10 * acoustic_fit
            + 0.10 * valence_sim
            + 0.05 * dance_sim
        )

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored = sorted(self.songs, key=lambda s: self._score(s, user), reverse=True)
        return scored[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append(f"genre matches your preference ({song.genre})")
        if song.mood == user.favorite_mood:
            reasons.append(f"mood matches ({song.mood})")
        if abs(song.energy - user.target_energy) < 0.2:
            reasons.append(f"energy level is close to your target ({song.energy:.2f} vs {user.target_energy:.2f})")
        if user.likes_acoustic and song.acousticness > 0.5:
            reasons.append(f"has strong acoustic character ({song.acousticness:.2f})")
        elif not user.likes_acoustic and song.acousticness < 0.5:
            reasons.append(f"has electronic/produced sound you prefer ({song.acousticness:.2f})")
        if abs(song.valence - user.target_valence) < 0.2:
            reasons.append(f"positivity level matches your vibe ({song.valence:.2f})")
        if not reasons:
            return f"'{song.title}' is a reasonable match based on overall profile similarity."
        return f"'{song.title}' by {song.artist}: " + ", ".join(reasons) + "."

SCORING_MODES: Dict[str, Dict[str, float]] = {
    "genre_first": {
        "genre": 0.27, "mood": 0.23, "energy": 0.18,
        "acoustic": 0.09, "valence": 0.09, "danceability": 0.04,
        "popularity": 0.03, "release_decade": 0.03,
        "instrumentalness": 0.02, "loudness": 0.01, "speechiness": 0.01,
    },
    "mood_first": {
        "genre": 0.15, "mood": 0.35, "energy": 0.18,
        "acoustic": 0.09, "valence": 0.09, "danceability": 0.04,
        "popularity": 0.03, "release_decade": 0.03,
        "instrumentalness": 0.02, "loudness": 0.01, "speechiness": 0.01,
    },
    "energy_focused": {
        "genre": 0.15, "mood": 0.15, "energy": 0.38,
        "acoustic": 0.09, "valence": 0.09, "danceability": 0.04,
        "popularity": 0.03, "release_decade": 0.03,
        "instrumentalness": 0.02, "loudness": 0.01, "speechiness": 0.01,
    },
}


def score_song(user_prefs: Dict, song: Dict, mode: str = "genre_first") -> Tuple[float, List[str]]:
    """Score a single song against user preferences using the given mode; return (score, reasons)."""
    w = SCORING_MODES.get(mode, SCORING_MODES["genre_first"])
    reasons = []
    score = 0.0

    if song.get("genre") == user_prefs.get("genre"):
        score += w["genre"]
        reasons.append(f"genre match (+{w['genre']:.2f})")

    if song.get("mood") == user_prefs.get("mood"):
        score += w["mood"]
        reasons.append(f"mood match (+{w['mood']:.2f})")

    target_energy = user_prefs.get("energy", 0.5)
    energy_contrib = w["energy"] * (1.0 - abs(song.get("energy", 0.5) - target_energy))
    score += energy_contrib
    if abs(song.get("energy", 0.5) - target_energy) < 0.2:
        reasons.append(f"energy close (+{energy_contrib:.2f})")

    likes_acoustic = user_prefs.get("likes_acoustic", False)
    acousticness = song.get("acousticness", 0.5)
    score += w["acoustic"] * (acousticness if likes_acoustic else 1.0 - acousticness)

    target_valence = user_prefs.get("valence", 0.5)
    valence_contrib = w["valence"] * (1.0 - abs(song.get("valence", 0.5) - target_valence))
    score += valence_contrib
    if abs(song.get("valence", 0.5) - target_valence) < 0.2:
        reasons.append(f"positivity close (+{valence_contrib:.2f})")

    target_dance = user_prefs.get("danceability", 0.5)
    score += w["danceability"] * (1.0 - abs(song.get("danceability", 0.5) - target_dance))

    target_pop = user_prefs.get("target_popularity", 0.5)
    score += w["popularity"] * (1.0 - abs(song.get("popularity", 50) / 100 - target_pop))

    preferred_decade = user_prefs.get("preferred_decade", 2010)
    score += w["release_decade"] * (1.0 - abs(song.get("release_decade", 2010) - preferred_decade) / 60)

    prefers_instrumental = user_prefs.get("prefers_instrumental", False)
    instr = song.get("instrumentalness", 0.5)
    score += w["instrumentalness"] * (instr if prefers_instrumental else 1.0 - instr)

    score += w["loudness"] * (1.0 - abs(song.get("loudness", 0.5) - user_prefs.get("target_loudness", 0.5)))
    score += w["speechiness"] * (1.0 - abs(song.get("speechiness", 0.5) - user_prefs.get("target_speechiness", 0.5)))

    return score, reasons


SAME_ARTIST_PENALTY = 0.20
SAME_GENRE_PENALTY = 0.10


def diversify(scored: List[Tuple[Song, float, List[str]]], k: int) -> List[Tuple[Song, float, List[str]]]:
    """Greedily select k songs, penalizing repeats of the same artist or genre."""
    k = min(k, len(scored))
    selected: List[Tuple[Song, float, List[str]]] = []
    remaining = list(scored)

    while len(selected) < k and remaining:
        best_idx = 0
        best_adjusted = float("-inf")
        for i, (song, score, reasons) in enumerate(remaining):
            penalty = sum(
                (SAME_ARTIST_PENALTY if song.artist == s.artist else 0.0) +
                (SAME_GENRE_PENALTY if song.genre == s.genre else 0.0)
                for s, _, _ in selected
            )
            if score - penalty > best_adjusted:
                best_adjusted = score - penalty
                best_idx = i
        selected.append(remaining.pop(best_idx))

    return selected


def load_songs(csv_path: str) -> List[Song]:
    """Read songs.csv and return a list of Song objects with numeric fields cast to float/int."""
    songs = []
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append(Song(
                id=int(row['id']),
                title=row['title'],
                artist=row['artist'],
                genre=row['genre'],
                mood=row['mood'],
                energy=float(row['energy']),
                tempo_bpm=float(row['tempo_bpm']),
                valence=float(row['valence']),
                danceability=float(row['danceability']),
                acousticness=float(row['acousticness']),
                popularity=float(row['popularity']),
                release_decade=int(row['release_decade']),
                instrumentalness=float(row['instrumentalness']),
                loudness=float(row['loudness']),
                speechiness=float(row['speechiness']),
            ))
    return songs

def recommend_songs(user_prefs: Dict, songs: List[Song], k: int = 5) -> List[Tuple[Song, float, List[str]]]:
    """Score every song with score_song, sort by score descending, and return the top k results."""
    scored = []
    for song in songs:
        song_dict = {
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "valence": song.valence,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
        }
        score, reasons = score_song(user_prefs, song_dict)
        scored.append((song, score, reasons))
    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]
