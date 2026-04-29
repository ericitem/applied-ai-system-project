import streamlit as st
from src.agent import run, AgentResult

st.set_page_config(page_title="VibeMatch", page_icon="🎵", layout="centered")
st.title("VibeMatch")
st.caption("Tell me what you're in the mood for — I'll find the songs.")

query = st.text_input(
    "What kind of music are you looking for?",
    placeholder="e.g. upbeat pop for a Friday night out",
    max_chars=500,
)

if st.button("Find songs", type="primary"):
    if not query.strip():
        st.warning("Please enter a request.")
    else:
        with st.spinner("Finding your songs..."):
            result: AgentResult = run(query)

        if result.error:
            st.error(result.error)
        else:
            st.subheader("Your recommendations")
            rows = [
                {"#": i, "Title": s.title, "Artist": s.artist,
                 "Genre": s.genre, "Mood": s.mood, "Score": f"{score:.2f}"}
                for i, (s, score, _) in enumerate(result.recommendations, 1)
            ]
            st.table(rows)

            st.subheader("Why these songs?")
            st.write(result.explanation)
