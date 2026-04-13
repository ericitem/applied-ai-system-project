# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0**

---

## 2. Intended Use

VibeMatch is designed to suggest songs from a small catalog based on a user's stated preferences: their favorite genre, current mood, preferred energy level, and whether they tend to like acoustic or electronic music.

It is intended for classroom exploration only. Its purpose is to demonstrate how a simple scoring algorithm can turn data about songs and listener preferences into a ranked list of recommendations, not to serve real users at scale.

It should **not** be used as a production recommendation system. It makes no attempt to learn from listening history, adapt over time, or handle the complexity of real musical taste.

---

## 3. How the Model Works

The system compares each song in the catalog to a user's preferences and gives it a score from 0 to 1. The higher the score, the better the match.

The score is built from six pieces of information about each song:

- **Genre:** worth 30% of the score. If the song's genre matches the user's favorite, it earns the full 30 points. If not, it earns zero. This is the single biggest factor.
- **Mood:** worth 25%. Same idea: full points for a match, zero for a miss.
- **Energy:** worth 20%. This is measured on a 0-1 scale. The closer a song's energy is to what the user wants, the more points it earns. A perfect match earns the full 20 points. A song that's far off earns fewer.
- **Acoustic character:** worth 10%. Users who prefer acoustic music score songs higher when they have more acoustic sound. Users who prefer electronic music score them higher when the sound is more produced.
- **Positivity (valence):** worth 10%. How upbeat or dark the song sounds, compared to what the user prefers.
- **Danceability:** worth 5%. A minor signal for how rhythmically engaging the song is.

Once every song has a score, the system sorts them from highest to lowest and returns the top results along with a short explanation of why each song ranked where it did.

---

## 4. Data

The catalog contains **18 songs** stored in a CSV file. Each song has a title, artist, genre, mood, and six numerical features: energy, tempo, valence, danceability, acousticness, and an ID.

**Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, r&b, electronic, country, metal, hip-hop, folk (13 genres total)

**Moods represented:** happy, chill, intense, relaxed, focused, moody, romantic, energetic, nostalgic, melancholic, sad (11 moods total)

**Limitations of the data:**

The catalog is very small. Some genres have multiple songs (lofi has 3, r&b has 2, jazz has 2, pop has 2) while others have only one (rock, metal, country, folk). A user who prefers rock has exactly one song that can earn the genre bonus. The system's recommendations are only as diverse as the catalog allows.

The mood labels were assigned manually and are subjective. Two people might reasonably describe the same song's mood differently, and the system treats labels as exact matches. "Intense" and "energetic" are treated as completely different even though they are close in meaning.

---

## 5. Strengths

The system works well when the user's preferences align with a well-represented genre in the catalog. A lofi listener, an ambient fan, or a pop listener gets confident, intuitive recommendations because multiple songs can compete for the top spots.

The scoring is transparent. Every recommendation comes with a plain-language explanation: "genre match (+0.30) | mood match (+0.25) | energy close (+0.19)", so there is no mystery about why a song appeared.

The system handles missing preferences gracefully. Fields like target valence and danceability default to neutral (0.5), so a user who only specifies genre and mood still gets reasonable results without errors.

---

## 6. Limitations and Bias

**Categorical dominance.** Genre (30%) and mood (25%) together make up 55% of the total score. A song that perfectly matches a user's energy, positivity, and danceability but belongs to the wrong genre will almost always rank below a mediocre song in the right genre. This makes the system feel reliable for clear genre preferences, but it means numerical nuance is mostly ignored when there are categorical matches available.

**The filter bubble.** Because the same small set of songs matches each profile, a given user will see the same recommendations every time. There is no randomness, no exploration, and no way to discover music outside the user's stated preferences. Real platforms deliberately inject variety to prevent this.

**Dataset imbalance.** The catalog has 3 lofi songs and 1 rock song. A lofi fan has three options competing for the top spot; a rock fan has one. The system is not equally capable across genres; it is better at recommending music it has more of.

**Mood labels are strict and subjective.** The system requires an exact string match for mood. "Melancholic" and "sad" score zero points for each other despite describing very similar emotional states. A user looking for melancholic metal found no mood match because the only metal song in the catalog is labeled "intense."

---

## 7. Evaluation

The system was tested with eight user profiles designed to cover both normal use and edge cases.

Normal profiles (high-energy pop, chill lofi, and deep intense rock) all produced intuitive results. Songs with matching genre, mood, and energy scored between 0.93 and 0.98, which is close to the theoretical maximum.

The most revealing edge cases were:

- **Conflicting preferences (high energy + sad folk):** The system ranked a quiet, low-energy folk song first because its genre and mood matched exactly, even though the user asked for high energy. This showed that categorical matches dominate even when numerical preferences are strongly violated.
- **Missing genre (classical):** No song in the catalog matched the genre, so the maximum achievable score dropped to 0.65. The system still returned something useful (a relaxed jazz song), but had no way to signal that it was working without its strongest feature.
- **Empty preferences:** With no genre, no mood, and neutral energy, the top score was 0.37. The system returned results, but they were essentially arbitrary.

One experiment was also run: swapping the genre weight (0.30 → 0.15) and energy weight (0.20 → 0.35). The top song stayed the same for both tested profiles, but lower-ranked results shifted; songs from adjacent genres with matching energy moved up. This confirmed that genre acts as a strong filter, and reducing its weight allows more cross-genre results to surface.

---

## 8. Future Work

**Expand and balance the catalog.** The most impactful improvement would be adding more songs, especially in underrepresented genres like rock, metal, country, and folk. Even doubling the catalog to 36 songs would meaningfully improve recommendation quality for users whose preferences are currently underserved.

**Add partial credit for similar categories.** Right now, "pop" and "indie pop" score zero against each other for genre, and "intense" and "energetic" score zero against each other for mood. A simple improvement would be to group related genres and moods so that near-matches earn partial points rather than nothing.

**Introduce diversity into the ranking.** The current system always returns the highest-scoring songs with no variation. Adding a small amount of randomness, or a rule that prevents the same artist from appearing twice in the top five, would make the recommendations feel less predictable and help users discover music outside their exact stated preferences.

---

## 9. Personal Reflection

*This section is yours to write in your own words. Here is a draft to react to and personalize:*

---

Building this recommender taught me that "smart-feeling" software does not require complex technology. The system I built is essentially a weighted checklist (six comparisons, a sum, a sort) and yet when it recommends "Sunrise City" for a pop fan with high energy, it feels surprisingly correct. That gap between simplicity and apparent intelligence was the most interesting thing I discovered.

Working through the five phases helped me understand that the hard part of recommendation systems is not the math but the design decisions. Choosing what to weight, how heavily, and what to leave out shapes the entire personality of the system. When I shifted genre weight down and energy up in Phase 4, the same songs mostly stayed on top, but the way the system "thought" about music changed. That felt like a real insight.

Claude helped me move quickly through implementation and documentation, but I had to stay engaged to make the outputs actually useful. The scoring explanations and README sections needed edits to sound like my voice, and the evaluation in Phase 4 required me to interpret the results, not just run them. The tool is most useful when you treat it as a thinking partner, not a shortcut.

If I continued this project, I would focus on making the catalog richer and smarter before touching the algorithm. Most of the system's limitations come from having 18 songs, not from the scoring formula. More songs, better mood labels, and a diversity rule in the ranking would make this feel like a real product rather than a simulation.

---
