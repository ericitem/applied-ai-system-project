"""
Command line runner for the Music Recommender Simulation.

Control variables:
  MODE      -- "genre_first", "mood_first", or "energy_focused"
  DIVERSITY -- True to penalize repeated artists/genres, False to rank by score only
"""

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

from src.recommender import load_songs, recommend_songs

MODE = "genre_first"   # change to "mood_first" or "energy_focused"
DIVERSITY = True


def main() -> None:
    songs = load_songs("data/songs.csv")

    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}

    recommendations = recommend_songs(user_prefs, songs, k=5, mode=MODE, diversity=DIVERSITY)

    genre = user_prefs.get("genre", "any")
    mood = user_prefs.get("mood", "any")
    energy = user_prefs.get("energy", 0.5)
    print(f"\nMode: {MODE} | Diversity: {DIVERSITY} | Profile: {genre} / {mood} / energy {energy}\n")

    rows = []
    for i, (song, score, reasons) in enumerate(recommendations, start=1):
        reason_str = " | ".join(reasons) if reasons else "overall match"
        rows.append([i, song.title, f"{score:.2f}", reason_str])

    headers = ["#", "Title", "Score", "Reasons"]
    if HAS_TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="simple"))
    else:
        print(f"{'#':<3} {'Title':<25} {'Score':<8} Reasons")
        print("-" * 70)
        for row in rows:
            print(f"{row[0]:<3} {row[1]:<25} {row[2]:<8} {row[3]}")
    print()


if __name__ == "__main__":
    main()
