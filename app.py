import html
import streamlit as st
from src.agent import run, AgentResult


def _hex_to_rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"{r},{g},{b}"


st.set_page_config(
    page_title="VibeMatch",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.stApp { background-color: #0f172a; color: #e2e8f0; }
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 0 !important;
    max-width: 680px !important;
    padding-bottom: 3rem !important;
}
section[data-testid="stSidebar"] { display: none; }

.stTextInput > div > div > input {
    background-color: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    padding: 10px 14px !important;
    font-size: 0.9rem !important;
}
.stTextInput > div > div > input::placeholder { color: #475569 !important; }
.stTextInput > div > div > input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.25) !important;
}
.stTextInput label { display: none; }

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    font-weight: 700 !important;
    padding: 10px !important;
    font-size: 0.9rem !important;
}
.stButton > button[kind="primary"]:hover { opacity: 0.88 !important; }

.stButton > button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 20px !important;
    color: #94a3b8 !important;
    font-size: 0.78rem !important;
    padding: 4px 12px !important;
}
.stButton > button:hover {
    background: rgba(99,102,241,0.2) !important;
    border-color: rgba(99,102,241,0.4) !important;
    color: #a5b4fc !important;
}

.streamlit-expanderHeader {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
    color: #64748b !important;
    font-size: 0.8rem !important;
}
.streamlit-expanderContent {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    padding: 10px 14px !important;
}

.stSpinner > div { border-top-color: #6366f1 !important; }
.stAlert { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []
if "liked" not in st.session_state:
    st.session_state.liked = set()
if "query_input" not in st.session_state:
    st.session_state.query_input = ""

st.markdown("""
<div style="background:linear-gradient(135deg,#1e1b4b 0%,#312e81 100%);
            padding:28px 24px 20px;text-align:center;
            margin:-1rem -1rem 1.5rem;
            border-bottom:1px solid rgba(255,255,255,0.08);">
  <div style="font-size:2.2rem;margin-bottom:6px;">🎵</div>
  <div style="color:#e0e7ff;font-size:1.5rem;font-weight:800;letter-spacing:0.04em;">VibeMatch</div>
  <div style="color:#818cf8;font-size:0.82rem;margin-top:5px;">Describe your mood · Get your songs</div>
</div>
""", unsafe_allow_html=True)

MOOD_PILLS = [
    ("😌 Chill",           "something chill and relaxing"),
    ("⚡ Workout",          "high energy workout music"),
    ("🎉 Party",            "upbeat party songs"),
    ("📚 Study",            "calm focused music for studying"),
    ("💔 Sad",              "melancholic and emotional songs"),
    ("🚗 Late Night Drive", "moody late night driving music"),
    ("☀️ Morning",          "uplifting morning feel-good songs"),
    ("🔥 Hype",             "intense hype music to get pumped up"),
]

PREF_COLORS = {
    "genre":                ("#6366f1", "#e0e7ff"),
    "mood":                 ("#10b981", "#d1fae5"),
    "energy":               ("#f59e0b", "#fef3c7"),
    "valence":              ("#f59e0b", "#fef3c7"),
    "danceability":         ("#f59e0b", "#fef3c7"),
    "likes_acoustic":       ("#06b6d4", "#cffafe"),
    "prefers_instrumental": ("#06b6d4", "#cffafe"),
}
PREF_LABELS = {
    "genre": "genre", "mood": "mood", "energy": "energy",
    "valence": "valence", "danceability": "dance",
    "likes_acoustic": "acoustic",
    "prefers_instrumental": "instrumental",
}
SHOW_PREFS = [
    "genre", "mood", "energy", "valence",
    "danceability", "likes_acoustic", "prefers_instrumental",
]

GENRE_EMOJI = {
    "pop": "🎤", "rock": "🎸", "lofi": "☕", "hip-hop": "🎧",
    "electronic": "⚡", "jazz": "🎷", "r&b": "🎶", "ambient": "🌙",
    "classical": "🎻", "country": "🤠", "metal": "🔥", "folk": "🪕",
    "indie pop": "🌸", "synthwave": "🌆", "reggae": "🌴", "blues": "🎺",
    "latin": "💃", "k-pop": "⭐",
}

st.markdown(
    '<p style="color:#475569;font-size:0.65rem;font-weight:700;'
    'letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px;">'
    'Quick picks</p>',
    unsafe_allow_html=True,
)
pill_cols = st.columns(4)
for idx, (label, pill_query) in enumerate(MOOD_PILLS):
    with pill_cols[idx % 4]:
        if st.button(label, key=f"pill_{idx}"):
            st.session_state["prefill"] = pill_query
            st.rerun()

st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

prefill_query = ""
if "prefill" in st.session_state:
    prefill_query = st.session_state.pop("prefill")
    st.session_state.query_input = prefill_query

query = st.text_input(
    "query",
    key="query_input",
    placeholder="e.g. something calm and low-key for studying at night",
    max_chars=500,
    label_visibility="collapsed",
)

do_search = (
    st.button("🔍 Find Songs", type="primary", use_container_width=True)
    or bool(prefill_query)
)

if st.session_state.history:
    with st.expander("🕐 Recent searches"):
        for idx, past_q in enumerate(reversed(st.session_state.history[-5:])):
            if st.button(f"↩ {past_q}", key=f"hist_{idx}"):
                st.session_state["prefill"] = past_q
                st.rerun()

if do_search:
    if not query.strip():
        st.warning("Please enter a music request.")
    else:
        if query not in st.session_state.history:
            st.session_state.history.append(query)

        with st.spinner("Finding your songs..."):
            result: AgentResult = run(query)

        if result.error:
            st.error(result.error)
        else:
            st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

            with st.expander("🤖 What VibeMatch understood"):
                if result.user_prefs:
                    badges = []
                    for key in SHOW_PREFS:
                        val = result.user_prefs.get(key)
                        if val is None:
                            continue
                        bg, _ = PREF_COLORS.get(key, ("#334155", "#e2e8f0"))
                        rgb = _hex_to_rgb(bg)
                        label = PREF_LABELS.get(key, key)
                        if isinstance(val, float):
                            display = f"{label}: {val:.2f}"
                        elif isinstance(val, bool):
                            display = f"{label}: {'yes' if val else 'no'}"
                        else:
                            display = f"{label}: {val}"
                        badges.append(
                            f'<span style="background:rgba({rgb},0.2);'
                            f'border:1px solid rgba({rgb},0.4);color:{bg};'
                            f'font-size:0.72rem;padding:3px 10px;border-radius:12px;'
                            f'margin:2px;display:inline-block;">{display}</span>'
                        )
                    st.markdown(
                        '<div style="display:flex;flex-wrap:wrap;gap:4px;padding:6px 0">'
                        + "".join(badges) + "</div>",
                        unsafe_allow_html=True,
                    )

            st.markdown(
                '<div style="color:#475569;font-size:0.65rem;font-weight:700;'
                'letter-spacing:0.08em;text-transform:uppercase;margin:16px 0 10px;">'
                'Your recommendations</div>',
                unsafe_allow_html=True,
            )

            for i, (song, score, reasons) in enumerate(result.recommendations, 1):
                genre_emoji = GENRE_EMOJI.get(song.genre, "🎵")
                score_pct = int(score * 100)
                reason_str = (
                    " · ".join(r.split(" (+")[0] for r in reasons)
                    if reasons else "overall match"
                )

                st.markdown(f"""
<div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.09);
            border-radius:12px;padding:14px 16px;margin-bottom:6px;">
  <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:8px;">
    <div style="display:flex;align-items:center;gap:10px;">
      <span style="color:#475569;font-size:0.75rem;font-weight:700;min-width:20px;">#{i}</span>
      <div>
        <div style="color:#e2e8f0;font-size:0.92rem;font-weight:700;">{genre_emoji} {song.title}</div>
        <div style="color:#64748b;font-size:0.75rem;margin-top:2px;">{song.artist}</div>
      </div>
    </div>
    <span style="color:#6366f1;font-size:0.9rem;font-weight:800;">{score:.2f}</span>
  </div>
  <div style="display:flex;gap:5px;flex-wrap:wrap;margin-bottom:8px;">
    <span style="background:rgba(99,102,241,0.2);border:1px solid rgba(99,102,241,0.35);
                 color:#818cf8;font-size:0.68rem;padding:2px 8px;border-radius:10px;">{song.genre}</span>
    <span style="background:rgba(16,185,129,0.2);border:1px solid rgba(16,185,129,0.35);
                 color:#34d399;font-size:0.68rem;padding:2px 8px;border-radius:10px;">{song.mood}</span>
    <span style="background:rgba(245,158,11,0.2);border:1px solid rgba(245,158,11,0.35);
                 color:#fbbf24;font-size:0.68rem;padding:2px 8px;border-radius:10px;">⚡ {song.energy:.2f}</span>
  </div>
  <div style="background:rgba(255,255,255,0.06);border-radius:4px;height:4px;margin-bottom:8px;">
    <div style="background:linear-gradient(90deg,#6366f1,#8b5cf6);border-radius:4px;
                height:4px;width:{score_pct}%;"></div>
  </div>
  <div style="color:#475569;font-size:0.68rem;font-style:italic;">{reason_str}</div>
</div>
""", unsafe_allow_html=True)

                btn_cols = st.columns([3, 1, 1])
                with btn_cols[0]:
                    if st.button("🔁 More like this", key=f"more_{i}"):
                        more_query = (
                            f"more songs like {song.title} by {song.artist}"
                            f" — {song.genre} {song.mood}"
                        )
                        st.session_state["prefill"] = more_query
                        st.rerun()
                with btn_cols[1]:
                    liked = song.title in st.session_state.liked
                    if st.button("❤️" if liked else "👍", key=f"like_{i}"):
                        st.session_state.liked = st.session_state.liked | {song.title}
                        st.rerun()
                with btn_cols[2]:
                    st.button("👎", key=f"dislike_{i}")

            st.markdown(f"""
<div style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2);
            border-radius:12px;padding:16px 18px;margin-top:8px;">
  <div style="color:#818cf8;font-size:0.65rem;font-weight:700;letter-spacing:0.08em;
              text-transform:uppercase;margin-bottom:8px;">✨ Why these songs?</div>
  <div style="color:#94a3b8;font-size:0.85rem;line-height:1.65;">{html.escape(result.explanation)}</div>
</div>
""", unsafe_allow_html=True)

            st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
