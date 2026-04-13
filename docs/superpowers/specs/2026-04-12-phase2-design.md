# Phase 2 Design — Music Recommender Simulation

## Context

Phase 2 expands the dataset, improves the user profile, and refines the scoring algorithm to use more of the available song features. All changes are applied directly to the codebase.

---

## Dataset Expansion

8 new songs added to `data/songs.csv` (18 total).

**New genres:** r&b, electronic, country, metal, hip-hop, folk  
**New moods:** romantic, energetic, nostalgic, melancholic, sad

| ID | Title | Artist | Genre | Mood | Energy |
|----|-------|--------|-------|------|--------|
| 11 | Golden Hour | Ray Sol | r&b | romantic | 0.65 |
| 12 | Digital Dreams | Byte Wave | electronic | energetic | 0.88 |
| 13 | Mountain Echo | Blue Ridge | country | nostalgic | 0.52 |
| 14 | Deep Blue | Sable Keys | jazz | melancholic | 0.31 |
| 15 | Thunder Fist | Iron Veil | metal | intense | 0.97 |
| 16 | Velvet Morning | Mara Cole | r&b | relaxed | 0.44 |
| 17 | Concrete Jungle | Grid King | hip-hop | energetic | 0.79 |
| 18 | Pine & Rain | Willow Creek | folk | sad | 0.33 |

---

## Additional Features Used in Scoring

The CSV already contained `valence` and `danceability` — these are now active in the scoring formula.

| Feature | What it represents | Why it helps |
|---|---|---|
| `valence` | Musical positivity (0 = dark/melancholic, 1 = upbeat/joyful) | Lets users express whether they want happy or sad music, independent of energy |
| `danceability` | Rhythmic suitability for dancing (0 = not danceable, 1 = very danceable) | Distinguishes workout music (high energy but not always danceable) from party music |
| `tempo_bpm` | Beats per minute | Stored in CSV, not yet scored — correlates with energy so low priority |

---

## User Profile Evaluation

**Original profile:** `favorite_genre`, `favorite_mood`, `target_energy`, `likes_acoustic`

**Critique:**
- Could not distinguish between an upbeat pop song and a melancholic pop song — same genre/mood/energy, very different emotional effect
- `likes_acoustic` was a binary field, which loses nuance (e.g., a user who mildly prefers acoustic)
- No way to express "I want danceable music" vs "I want mellow music at similar energy"

**Changes made:**
- Added `target_valence: float = 0.5` — optional, defaults to neutral
- Added `target_danceability: float = 0.5` — optional, defaults to neutral
- Both fields are optional with defaults so existing tests and code are unaffected

---

## Scoring Algorithm

Weighted sum, max = 1.0:

| Feature | Weight | Formula |
|---|---|---|
| genre match | 0.30 | binary |
| mood match | 0.25 | binary |
| energy similarity | 0.20 | `1.0 - abs(diff)` |
| acoustic fit | 0.10 | acousticness or inverse |
| valence similarity | 0.10 | `1.0 - abs(diff)` |
| danceability similarity | 0.05 | `1.0 - abs(diff)` |

**Tradeoffs:**
- Genre reduced from 0.35 → 0.30 to make room for valence and danceability
- Energy reduced from 0.25 → 0.20 for same reason
- Genre + mood together still dominate at 55% — correct, since categorical fit is the strongest signal

---

## Potential Biases

- **Genre dominance:** A song in the wrong genre is heavily penalized even if all numerical features are ideal
- **Binary categorical matching:** "indie pop" and "pop" score 0 for genre match — no partial credit
- **Small catalog:** 18 songs means some profiles have no good match available
- **Default valence/danceability = 0.5:** Users who don't specify these get a neutral preference, which slightly favors mid-range songs

---

## Files Changed

- `data/songs.csv` — 8 new songs added
- `src/recommender.py` — `UserProfile` expanded; `_score` uses 6 features; weights rebalanced
- `README.md` — "How The System Works" section updated with full tables, algorithm recipe, bias note, Mermaid diagram
