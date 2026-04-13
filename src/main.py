"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    print(f"{'#':<3} {'Title':<25} {'Score':<8} Reasons")
    print("-" * 70)
    for i, (song, score, reasons) in enumerate(recommendations, start=1):
        reason_str = " | ".join(reasons) if reasons else "overall profile match"
        print(f"{i:<3} {song.title:<25} {score:<8.2f} {reason_str}")


if __name__ == "__main__":
    main()
