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

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a single song against user preferences; return (score, reasons)."""
    reasons = []
    score = 0.0

    # Categorical matches
    if song.get("genre") == user_prefs.get("genre"):
        points = 0.30
        score += points
        reasons.append(f"genre match (+{points:.2f})")

    if song.get("mood") == user_prefs.get("mood"):
        points = 0.25
        score += points
        reasons.append(f"mood match (+{points:.2f})")

    # Numerical similarity — each uses 1.0 - |diff| scaled by weight
    target_energy = user_prefs.get("energy", 0.5)
    energy_contrib = 0.20 * (1.0 - abs(song.get("energy", 0.5) - target_energy))
    score += energy_contrib
    if abs(song.get("energy", 0.5) - target_energy) < 0.2:
        reasons.append(f"energy close (+{energy_contrib:.2f})")

    likes_acoustic = user_prefs.get("likes_acoustic", False)
    acousticness = song.get("acousticness", 0.5)
    acoustic_contrib = 0.10 * (acousticness if likes_acoustic else 1.0 - acousticness)
    score += acoustic_contrib

    target_valence = user_prefs.get("valence", 0.5)
    valence_contrib = 0.10 * (1.0 - abs(song.get("valence", 0.5) - target_valence))
    score += valence_contrib
    if abs(song.get("valence", 0.5) - target_valence) < 0.2:
        reasons.append(f"positivity close (+{valence_contrib:.2f})")

    target_dance = user_prefs.get("danceability", 0.5)
    dance_contrib = 0.05 * (1.0 - abs(song.get("danceability", 0.5) - target_dance))
    score += dance_contrib

    return score, reasons


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
