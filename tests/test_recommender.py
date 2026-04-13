from src.recommender import Song, UserProfile, Recommender, score_song, recommend_songs, load_songs, diversify

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# --- Phase 3 tests ---

def test_score_song_returns_tuple_of_score_and_reasons():
    """score_song should return (float, list)."""
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    song = {"genre": "pop", "mood": "happy", "energy": 0.8,
            "valence": 0.8, "danceability": 0.7, "acousticness": 0.2}
    result = score_song(user_prefs, song)
    assert isinstance(result, tuple)
    assert len(result) == 2
    score, reasons = result
    assert isinstance(score, float)
    assert isinstance(reasons, list)


def test_score_song_genre_match_increases_score():
    """A genre match should produce a higher score than a genre miss."""
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    match = {"genre": "pop", "mood": "happy", "energy": 0.8,
             "valence": 0.8, "danceability": 0.7, "acousticness": 0.2}
    miss  = {"genre": "lofi", "mood": "happy", "energy": 0.8,
             "valence": 0.8, "danceability": 0.7, "acousticness": 0.2}
    score_match, _ = score_song(user_prefs, match)
    score_miss, _  = score_song(user_prefs, miss)
    assert score_match > score_miss


def test_score_song_reasons_mention_genre_on_match():
    """When genre matches, reasons list should contain a genre entry."""
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    song = {"genre": "pop", "mood": "happy", "energy": 0.8,
            "valence": 0.8, "danceability": 0.7, "acousticness": 0.2}
    _, reasons = score_song(user_prefs, song)
    assert any("genre" in r.lower() for r in reasons)


def test_score_song_reasons_mention_mood_on_match():
    """When mood matches, reasons list should contain a mood entry."""
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    song = {"genre": "pop", "mood": "happy", "energy": 0.8,
            "valence": 0.8, "danceability": 0.7, "acousticness": 0.2}
    _, reasons = score_song(user_prefs, song)
    assert any("mood" in r.lower() for r in reasons)


def test_recommend_songs_returns_sorted_results():
    """recommend_songs should return results with the highest score first."""
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    songs = [
        Song(id=1, title="Pop Hit", artist="A", genre="pop", mood="happy",
             energy=0.8, tempo_bpm=120, valence=0.9, danceability=0.8, acousticness=0.2),
        Song(id=2, title="Lofi Beat", artist="B", genre="lofi", mood="chill",
             energy=0.4, tempo_bpm=80, valence=0.6, danceability=0.5, acousticness=0.9),
    ]
    results = recommend_songs(user_prefs, songs, k=2)
    assert len(results) == 2
    scores = [score for _, score, _ in results]
    assert scores[0] >= scores[1]


def test_recommend_songs_result_includes_reasons_list():
    """Each result from recommend_songs should include a reasons list."""
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    songs = [
        Song(id=1, title="Pop Hit", artist="A", genre="pop", mood="happy",
             energy=0.8, tempo_bpm=120, valence=0.9, danceability=0.8, acousticness=0.2),
    ]
    results = recommend_songs(user_prefs, songs, k=1)
    _, _, reasons = results[0]
    assert isinstance(reasons, list)
    assert len(reasons) > 0


def test_mood_first_mode_weights_mood_above_genre():
    """In mood_first mode, a mood match should outscore a genre match."""
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.5}
    genre_only = {"genre": "pop", "mood": "chill", "energy": 0.5,
                  "valence": 0.5, "danceability": 0.5, "acousticness": 0.5,
                  "popularity": 50, "release_decade": 2010,
                  "instrumentalness": 0.5, "loudness": 0.5, "speechiness": 0.5}
    mood_only  = {"genre": "lofi", "mood": "happy", "energy": 0.5,
                  "valence": 0.5, "danceability": 0.5, "acousticness": 0.5,
                  "popularity": 50, "release_decade": 2010,
                  "instrumentalness": 0.5, "loudness": 0.5, "speechiness": 0.5}
    score_genre, _ = score_song(user_prefs, genre_only, mode="mood_first")
    score_mood, _  = score_song(user_prefs, mood_only,  mode="mood_first")
    assert score_mood > score_genre


def test_diversify_prefers_different_artist_over_same_artist():
    """When two songs from the same artist compete with one from a different artist,
    the second same-artist song should be pushed below the different-artist song."""
    artist_a1 = Song(id=1, title="A Hit 1", artist="ArtistA", genre="pop", mood="happy",
                     energy=0.8, tempo_bpm=120, valence=0.9, danceability=0.8, acousticness=0.2)
    artist_a2 = Song(id=2, title="A Hit 2", artist="ArtistA", genre="pop", mood="chill",
                     energy=0.7, tempo_bpm=110, valence=0.7, danceability=0.7, acousticness=0.3)
    artist_b1 = Song(id=3, title="B Track", artist="ArtistB", genre="rock", mood="intense",
                     energy=0.6, tempo_bpm=130, valence=0.5, danceability=0.6, acousticness=0.1)

    # A1 scores highest, A2 slightly above B — without diversity, order is A1, A2, B
    # With diversity, A2 gets SAME_ARTIST_PENALTY (0.20): 0.75 - 0.20 = 0.55 < B's 0.70
    # So order should be A1, B
    scored = [
        (artist_a1, 0.90, ["genre match"]),
        (artist_a2, 0.75, ["energy close"]),
        (artist_b1, 0.70, ["energy close"]),
    ]
    result = diversify(scored, k=2)
    titles = [song.title for song, _, _ in result]
    assert titles[0] == "A Hit 1"
    assert titles[1] == "B Track"


def test_diversify_returns_k_songs():
    """diversify should return exactly k songs."""
    songs = [
        Song(id=i, title=f"Song {i}", artist=f"Artist{i}", genre="pop", mood="happy",
             energy=0.5, tempo_bpm=100, valence=0.5, danceability=0.5, acousticness=0.5)
        for i in range(1, 6)
    ]
    scored = [(s, 1.0 - i * 0.1, []) for i, s in enumerate(songs)]
    result = diversify(scored, k=3)
    assert len(result) == 3


def test_energy_focused_mode_weights_energy_above_genre():
    """In energy_focused mode, a close energy match should outscore a genre match with far energy."""
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    genre_far_energy = {"genre": "pop", "mood": "chill", "energy": 0.2,
                        "valence": 0.5, "danceability": 0.5, "acousticness": 0.5,
                        "popularity": 50, "release_decade": 2010,
                        "instrumentalness": 0.5, "loudness": 0.5, "speechiness": 0.5}
    no_genre_close_energy = {"genre": "lofi", "mood": "chill", "energy": 0.82,
                              "valence": 0.5, "danceability": 0.5, "acousticness": 0.5,
                              "popularity": 50, "release_decade": 2010,
                              "instrumentalness": 0.5, "loudness": 0.5, "speechiness": 0.5}
    score_genre, _ = score_song(user_prefs, genre_far_energy,    mode="energy_focused")
    score_energy, _ = score_song(user_prefs, no_genre_close_energy, mode="energy_focused")
    assert score_energy > score_genre


def test_recommend_songs_diversity_flag_reduces_same_artist_repeats():
    """With diversity=True, recommend_songs should not return two songs from the same artist
    when a different-artist option with a reasonable score exists."""
    songs = [
        Song(id=1, title="Pop Hit 1", artist="Neon Echo", genre="pop", mood="happy",
             energy=0.8, tempo_bpm=120, valence=0.9, danceability=0.8, acousticness=0.2),
        Song(id=2, title="Pop Hit 2", artist="Neon Echo", genre="pop", mood="happy",
             energy=0.78, tempo_bpm=118, valence=0.85, danceability=0.78, acousticness=0.22),
        Song(id=3, title="Other Track", artist="ArtistB", genre="pop", mood="happy",
             energy=0.75, tempo_bpm=115, valence=0.80, danceability=0.75, acousticness=0.25),
    ]
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    # Pre-condition: without diversity, both top-2 slots should be Neon Echo
    baseline = recommend_songs(user_prefs, songs, k=2, diversity=False)
    assert [s.artist for s, _, _ in baseline].count("Neon Echo") == 2
    # With diversity, ArtistB should displace the second Neon Echo slot
    results = recommend_songs(user_prefs, songs, k=2, diversity=True)
    artists = [song.artist for song, _, _ in results]
    assert "Neon Echo" in artists
    assert "ArtistB" in artists
