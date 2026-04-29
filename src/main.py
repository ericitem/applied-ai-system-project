"""
Command line runner for VibeMatch.

Without --query: runs the original rules-based flow with hardcoded preferences.
With --query:    runs the full AI pipeline (interpreter → recommender → explainer).
"""
import argparse

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

from src.recommender import load_songs, recommend_songs

MODE = "genre_first"
DIVERSITY = True


def _run_rules_based() -> None:
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


def _run_ai(query: str) -> None:
    from src.agent import run, AgentResult
    result: AgentResult = run(query)

    if result.error:
        print(f"\nError: {result.error}\n")
        return

    print(f"\nQuery: {query}\n")
    rows = []
    for i, (song, score, reasons) in enumerate(result.recommendations, start=1):
        reason_str = " | ".join(reasons) if reasons else "overall match"
        rows.append([i, song.title, song.artist, f"{score:.2f}", reason_str])

    headers = ["#", "Title", "Artist", "Score", "Reasons"]
    if HAS_TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="simple"))
    else:
        print(f"{'#':<3} {'Title':<25} {'Artist':<20} {'Score':<8} Reasons")
        print("-" * 80)
        for row in rows:
            print(f"{row[0]:<3} {row[1]:<25} {row[2]:<20} {row[3]:<8} {row[4]}")

    print(f"\n{result.explanation}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="VibeMatch Music Recommender")
    parser.add_argument("--query", type=str, default=None,
                        help="Natural language music request (uses AI pipeline)")
    args = parser.parse_args()

    if args.query:
        _run_ai(args.query)
    else:
        _run_rules_based()


if __name__ == "__main__":
    main()
