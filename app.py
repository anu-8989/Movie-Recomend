import html
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests
import streamlit as st

# =============================
# CONFIG
# =============================
API_BASE = "https://movie-rec-466x.onrender.com" or "http://127.0.0.1:8000"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# =============================
# STYLES (dark cinema, interactive)
# Palette: ink #13111f | surface #1d1a30 | line #2e2a4a | text #ece9ff
#          muted #a39fc4 | accent (velvet rose) #ff4d6d | accent-2 (cool glow) #6ee7f9
# =============================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&family=Poppins:wght@500;600;700&display=swap');

:root {
  --ink: #13111f; --surface: #1d1a30; --line: #2e2a4a;
  --text: #ece9ff; --muted: #a39fc4;
  --accent: #ff4d6d; --accent2: #6ee7f9;
}

html, body, .stApp,
.stApp :is(p, span, div, label, li, input, button, textarea, a, td, th, small, summary):not([data-testid="stIconMaterial"]):not([class*="material" i]) {
  font-family: 'Nunito', system-ui, sans-serif !important;
}
.stApp p, .stApp li, .stApp label { font-size: 1.02rem; line-height: 1.6; font-weight: 500; }
.stApp {
  background:
    radial-gradient(900px 420px at 85% -10%, rgba(255,77,109,0.16), transparent 60%),
    radial-gradient(700px 380px at 0% 0%, rgba(110,231,249,0.08), transparent 60%),
    var(--ink);
  color: var(--text);
}
.stApp p, .stApp label, .stApp span, .stApp li, .stApp div[data-testid="stMarkdownContainer"] { color: var(--text); }
h1, h2, h3, h4, .stApp h1, .stApp h2, .stApp h3, .stApp h4 { font-family: 'Poppins', 'Nunito', sans-serif !important; font-weight: 600 !important; color: var(--text) !important; letter-spacing: 0; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1400px; }
hr { border-color: var(--line) !important; }

/* ---------- top bar ---------- */
.topbar { display:flex; align-items:center; gap:16px; padding: 6px 0 4px 0; }
.logo {
  width:56px; height:56px; border-radius:16px; display:flex; align-items:center; justify-content:center;
  font-size:28px; background: linear-gradient(135deg, var(--accent), #b5179e);
  box-shadow: 0 10px 30px rgba(255,77,109,0.35); transition: transform .35s ease;
}
.logo:hover { transform: rotate(-8deg) scale(1.08); }
.brand { font-family:'Poppins',sans-serif !important; font-weight:600; font-size:2rem; line-height:1.15; color: var(--text); }
.small-muted { color: var(--muted) !important; font-size: 0.92rem; }

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--line); }
section[data-testid="stSidebar"] * { color: var(--text); }
section[data-testid="stSidebar"] h2 { font-size: 1.45rem; margin-bottom: 2px; }
section[data-testid="stSidebar"] h3 { font-size: 1.1rem; }
section[data-testid="stSidebar"] .small-muted { color: var(--muted) !important; margin-bottom: 14px; }

/* ---------- inputs ---------- */
div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
  background: var(--surface) !important; border: 1px solid var(--line) !important;
  border-radius: 14px !important; transition: border-color .2s, box-shadow .2s;
}
div[data-baseweb="input"] > div:focus-within, div[data-baseweb="select"] > div:hover {
  border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(255,77,109,0.18);
}
div[data-baseweb="input"] input { color: var(--text) !important; font-size: 1.02rem; }
ul[role="listbox"], div[data-baseweb="popover"] > div { background: var(--surface) !important; border-radius: 12px; }
li[role="option"]:hover { background: rgba(255,77,109,0.18) !important; }

/* ---------- buttons ---------- */
.stButton > button {
  width: 100%; border-radius: 999px; padding: 0.35rem 1rem; font-weight: 600;
  background: transparent; color: var(--text); border: 1px solid var(--line);
  transition: all .22s ease;
}
.stButton > button:hover {
  background: var(--accent); border-color: var(--accent); color: #fff;
  transform: translateY(-2px); box-shadow: 0 8px 22px rgba(255,77,109,0.35);
}
.stButton > button:active { transform: translateY(0) scale(0.98); }
.stButton > button:focus-visible { outline: 2px solid var(--accent2); outline-offset: 2px; }

/* ---------- poster cards ---------- */
div[data-testid="stImage"] img {
  border-radius: 14px; border: 1px solid var(--line);
  transition: transform .3s ease, box-shadow .3s ease, border-color .3s ease;
}
div[data-testid="stImage"] img:hover {
  transform: translateY(-6px) scale(1.035); border-color: var(--accent);
  box-shadow: 0 18px 40px rgba(255,77,109,0.28);
}
.movie-title {
  font-size: 0.9rem; line-height: 1.15rem; height: 2.3rem; overflow: hidden;
  margin: 8px 0 6px 0; font-weight: 500; color: var(--text);
}
.no-poster {
  aspect-ratio: 2/3; border-radius: 14px; border: 1px dashed var(--line); color: var(--muted);
  display:flex; align-items:center; justify-content:center; font-size: 0.9rem;
}

/* ---------- details ---------- */
.card { border: 1px solid var(--line); border-radius: 18px; padding: 16px; background: var(--surface); }
.hero {
  border: 1px solid var(--line); border-radius: 22px; padding: 28px 30px; min-height: 360px;
  background-size: cover; background-position: center;
}
.hero h2 { margin: 0 0 10px 0; font-size: 2.3rem; }
.hero p { max-width: 70ch; line-height: 1.65; color: #d9d5f5; }
.chip {
  display:inline-block; padding: 4px 12px; margin: 0 8px 8px 0; border-radius: 999px; font-size: 0.82rem;
  border: 1px solid rgba(255,255,255,0.18); background: rgba(255,255,255,0.06); color: var(--text);
  transition: all .2s ease;
}
.chip:hover { background: var(--accent); border-color: var(--accent); transform: translateY(-1px); }
.chip.date { border-color: var(--accent2); color: var(--accent2); }

/* ---------- tabs ---------- */
button[data-baseweb="tab"] { font-weight: 600; color: var(--muted); transition: color .2s; }
button[data-baseweb="tab"]:hover { color: var(--text); }
button[data-baseweb="tab"][aria-selected="true"] { color: var(--text); }
div[data-baseweb="tab-highlight"] { background-color: var(--accent) !important; }
div[data-baseweb="tab-border"] { background-color: var(--line) !important; }

/* ---------- no loading indicators ---------- */
[data-testid="stStatusWidget"], [data-testid="stSpinner"], .stSpinner { display: none !important; }
[data-stale="true"], .stale-element { opacity: 1 !important; transition: none !important; }

/* ---------- interactive icons ---------- */
@keyframes wiggle { 0%,100% { transform: rotate(0); } 25% { transform: rotate(-16deg); } 75% { transform: rotate(16deg); } }
@keyframes pop { 0% { transform: scale(1); } 50% { transform: scale(1.4) rotate(-8deg); } 100% { transform: scale(1); } }
@keyframes spin360 { to { transform: rotate(360deg); } }
@keyframes nudge { 50% { transform: translateX(5px); } }
@keyframes bob { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }

.ico, .reel, .em { display: inline-block; cursor: default; }
.ico { margin-right: 6px; }
.ico:hover { animation: pop .45s ease; }
h2:hover .ico, h3:hover .ico, h4:hover .ico { animation: wiggle .6s ease; }
.reel { animation: bob 3s ease-in-out infinite; }
.logo:hover .reel { animation: spin360 .8s ease; }
.chip .em { margin-right: 5px; transition: transform .25s; }
.chip:hover .em { animation: pop .45s ease; }
.stButton > button p { margin: 0; }
.stButton > button:hover p { animation: nudge .5s ease; }
button[data-baseweb="tab"]:hover p { animation: wiggle .5s ease; }

@media (prefers-reduced-motion: reduce) {
  .ico, .reel, .em, .stButton > button p, button[data-baseweb="tab"] p { animation: none !important; }
  * { transition: none !important; }
}
</style>
""",
    unsafe_allow_html=True,
)

# =============================
# STATE + ROUTING (single-file pages)
# =============================
if "view" not in st.session_state:
    st.session_state.view = "home"  # home | details
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None

# Read the URL only once per session (deep links still work).
# After that, session_state is the single source of truth, so a stale URL
# can never pull the user back to the details page.
if "route_initialized" not in st.session_state:
    st.session_state.route_initialized = True
    qp_view = st.query_params.get("view")
    qp_id = st.query_params.get("id")
    if qp_view in ("home", "details"):
        st.session_state.view = qp_view
    if qp_id:
        try:
            st.session_state.selected_tmdb_id = int(qp_id)
            st.session_state.view = "details"
        except:
            pass


def nav_home():
    """Button callback: runs before the next rerun, so Back works instantly."""
    st.session_state.view = "home"
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]


def nav_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))


def goto_home():
    nav_home()
    st.rerun()


def goto_details(tmdb_id: int):
    nav_details(tmdb_id)
    st.rerun()


# =============================
# API HELPERS
# =============================
@st.cache_resource
def _api_store():
    return {
        "pool": ThreadPoolExecutor(max_workers=8),
        "cache": {},
        "pending": {},
        "lock": threading.Lock(),
    }


def _request(path: str, params: dict | None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}: {r.text[:300]}"
        return r.json(), None
    except Exception as e:
        return None, f"Request failed: {e}"


def api_get_json(path: str, params: dict | None = None, ttl: int = 30):
    """Same result as before (data, err) with a short cache.
    The request runs in a background thread while we poll, so the app can
    still react to a Back / Home click while the API is slow."""
    store = _api_store()
    key = (path, json.dumps(params or {}, sort_keys=True, default=str))

    with store["lock"]:
        hit = store["cache"].get(key)
        if hit and time.time() - hit[0] < ttl:
            return hit[1]
        fut = store["pending"].get(key)
        if fut is None:
            fut = store["pool"].submit(_request, path, params)
            store["pending"][key] = fut

    tick = st.sidebar.empty()  # invisible; lets Streamlit process a new click
    while not fut.done():
        time.sleep(0.05)
        tick.empty()

    result = fut.result()
    with store["lock"]:
        store["pending"].pop(key, None)
        store["cache"][key] = (time.time(), result)
    return result


GENRE_EMOJI = {
    "Action": "💥", "Adventure": "🧭", "Animation": "🎨", "Comedy": "😂", "Crime": "🕵️",
    "Documentary": "🎞️", "Drama": "🎭", "Family": "👨‍👩‍👧", "Fantasy": "🧙", "History": "📜",
    "Horror": "👻", "Music": "🎵", "Mystery": "🔍", "Romance": "💖", "Science Fiction": "🚀",
    "TV Movie": "📺", "Thriller": "😱", "War": "⚔️", "Western": "🤠",
}
CATEGORY_EMOJI = {
    "trending": "🔥", "popular": "⭐", "top_rated": "🏆", "now_playing": "🎟️", "upcoming": "⏳",
}


def show_image(url):
    # works on both newer and older Streamlit versions
    try:
        st.image(url, use_container_width=True)
    except TypeError:
        st.image(url, use_column_width=True)


def poster_grid(cards, cols=6, key_prefix="grid"):
    if not cards:
        st.info("No movies to show.")
        return

    rows = (len(cards) + cols - 1) // cols
    idx = 0
    for r in range(rows):
        colset = st.columns(cols)
        for c in range(cols):
            if idx >= len(cards):
                break
            m = cards[idx]
            idx += 1

            tmdb_id = m.get("tmdb_id")
            title = m.get("title", "Untitled")
            poster = m.get("poster_url")

            with colset[c]:
                if poster:
                    show_image(poster)
                else:
                    st.markdown(
                        "<div class='no-poster'>🖼️ No poster</div>",
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    f"<div class='movie-title' title='{html.escape(title, quote=True)}'>{html.escape(title)}</div>",
                    unsafe_allow_html=True,
                )

                st.button(
                    "▶ Open",
                    key=f"{key_prefix}_{r}_{c}_{idx}_{tmdb_id}",
                    on_click=nav_details,
                    args=(tmdb_id,),
                    disabled=not tmdb_id,
                )


def to_cards_from_tfidf_items(items):
    """Accepts nested {"tmdb": {...}}, flat {"tmdb_id": ...} or raw TMDB {"id", "poster_path"} items."""
    cards = []
    for x in items or []:
        if not isinstance(x, dict):
            continue
        tmdb = x.get("tmdb") if isinstance(x.get("tmdb"), dict) else {}
        tmdb_id = tmdb.get("tmdb_id") or tmdb.get("id") or x.get("tmdb_id") or x.get("id")
        if not tmdb_id:
            continue
        poster = tmdb.get("poster_url") or x.get("poster_url")
        if not poster:
            path = tmdb.get("poster_path") or x.get("poster_path")
            poster = f"{TMDB_IMG}{path}" if path else None
        cards.append(
            {
                "tmdb_id": int(tmdb_id),
                "title": tmdb.get("title") or x.get("title") or "Untitled",
                "poster_url": poster,
            }
        )
    return cards


# =============================
# IMPORTANT: Robust TMDB search parsing
# Supports BOTH API shapes:
# 1) raw TMDB: {"results":[{id,title,poster_path,...}]}
# 2) list cards: [{tmdb_id,title,poster_url,...}]
# =============================
def parse_tmdb_search_to_cards(data, keyword: str, limit: int = 24):
    """
    Returns:
      suggestions: list[(label, tmdb_id)]
      cards: list[{tmdb_id,title,poster_url}]
    """
    keyword_l = keyword.strip().lower()

    # A) If API returns dict with 'results'
    if isinstance(data, dict) and "results" in data:
        raw = data.get("results") or []
        raw_items = []
        for m in raw:
            title = (m.get("title") or "").strip()
            tmdb_id = m.get("id")
            poster_path = m.get("poster_path")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": f"{TMDB_IMG}{poster_path}" if poster_path else None,
                    "release_date": m.get("release_date", ""),
                }
            )

    # B) If API returns already as list
    elif isinstance(data, list):
        raw_items = []
        for m in data:
            # might be {tmdb_id,title,poster_url}
            tmdb_id = m.get("tmdb_id") or m.get("id")
            title = (m.get("title") or "").strip()
            poster_url = m.get("poster_url")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": poster_url,
                    "release_date": m.get("release_date", ""),
                }
            )
    else:
        return [], []

    # Word-match filtering (contains)
    matched = [x for x in raw_items if keyword_l in x["title"].lower()]

    # If nothing matched, fallback to raw list (so never blank)
    final_list = matched if matched else raw_items

    # Suggestions = top 10 labels
    suggestions = []
    for x in final_list[:10]:
        year = (x.get("release_date") or "")[:4]
        label = f"{x['title']} ({year})" if year else x["title"]
        suggestions.append((label, x["tmdb_id"]))

    # Cards = top N
    cards = [
        {"tmdb_id": x["tmdb_id"], "title": x["title"], "poster_url": x["poster_url"]}
        for x in final_list[:limit]
    ]
    return suggestions, cards


# =============================
# SIDEBAR
# =============================
CATEGORY_LABELS = {
    "trending": "🔥 Hot right now",
    "popular": "⭐ Everyone's watching",
    "top_rated": "🏆 All-time best",
    "now_playing": "🎟️ In theatres now",
    "upcoming": "⏳ Coming soon",
}

with st.sidebar:
    st.markdown(
        "<h2><span class='ico'>👋</span>Hey there!</h2>"
        "<div class='small-muted'>Not sure what to watch? Let's find something good.</div>",
        unsafe_allow_html=True,
    )
    st.button("🏠 Take me home", on_click=nav_home, key="nav_home_sidebar")

    st.markdown("---")
    st.markdown(
        "<h3><span class='ico'>🍿</span>What's on today?</h3>", unsafe_allow_html=True
    )
    home_category = st.selectbox(
        "Pick your vibe",
        list(CATEGORY_LABELS.keys()),
        index=0,
        format_func=lambda k: CATEGORY_LABELS[k],
    )
    grid_cols = st.slider("Posters per row", 4, 8, 6)

# =============================
# HEADER
# =============================
st.markdown(
    "<div class='topbar'><div class='logo'><span class='reel'>🎬</span></div><div>"
    "<div class='brand'>Movie Recommender</div>"
    "<div class='small-muted'>Search a title, pick a suggestion, and discover movies you'll love.</div>"
    "</div></div>",
    unsafe_allow_html=True,
)
st.divider()

# ==========================================================
# VIEW: HOME
# ==========================================================
if st.session_state.view == "home":
    typed = st.text_input(
        "Search by movie title (keyword)", placeholder="Type: avenger, batman, love..."
    )

    st.divider()

    # SEARCH MODE (Autocomplete + word-match results)
    if typed.strip():
        if len(typed.strip()) < 2:
            st.caption("Type at least 2 characters for suggestions.")
        else:
            data, err = api_get_json(
                "/tmdb/search", params={"query": typed.strip()}
            )

            if err or data is None:
                st.error(f"Search failed: {err}")
            else:
                suggestions, cards = parse_tmdb_search_to_cards(
                    data, typed.strip(), limit=24
                )

                # Dropdown
                if suggestions:
                    labels = ["-- Select a movie --"] + [s[0] for s in suggestions]
                    selected = st.selectbox("Suggestions", labels, index=0)

                    if selected != "-- Select a movie --":
                        # map label -> id
                        label_to_id = {s[0]: s[1] for s in suggestions}
                        goto_details(label_to_id[selected])
                else:
                    st.info("No suggestions found. Try another keyword.")

                st.markdown(f"<h3><span class='ico'>🔎</span>Results · {len(cards)}</h3>", unsafe_allow_html=True)
                poster_grid(cards, cols=grid_cols, key_prefix="search_results")

        st.stop()

    # HOME FEED MODE
    st.markdown(
        f"<h3><span class='ico'>{CATEGORY_EMOJI.get(home_category, '🏠')}</span>"
        f"{home_category.replace('_',' ').title()}</h3>",
        unsafe_allow_html=True,
    )

    home_cards, err = api_get_json(
        "/home", params={"category": home_category, "limit": 24}
    )
    if err or not home_cards:
        st.error(f"Home feed failed: {err or 'Unknown error'}")
        st.stop()

    poster_grid(home_cards, cols=grid_cols, key_prefix="home_feed")

# ==========================================================
# VIEW: DETAILS
# ==========================================================
elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.warning("No movie selected.")
        st.button("← Back to home", on_click=nav_home, key="back_empty")
        st.stop()

    # Top bar
    a, b = st.columns([3, 1])
    with a:
        st.markdown("<h3><span class='ico'>🎞️</span>Movie details</h3>", unsafe_allow_html=True)
    with b:
        st.button("← Back to home", on_click=nav_home, key="back_details")

    # Details (your FastAPI safe route)
    data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        st.stop()

    # Layout: Poster LEFT, Details RIGHT (backdrop is the hero background)
    left, right = st.columns([1, 2.4], gap="large")

    with left:
        if data.get("poster_url"):
            show_image(data["poster_url"])
        else:
            st.markdown(
                "<div class='no-poster'>🖼️ No poster</div>", unsafe_allow_html=True
            )

    with right:
        title_txt = html.escape(data.get("title", "") or "")
        release = html.escape(data.get("release_date") or "-")
        genre_names = [g["name"] for g in data.get("genres", [])]
        genre_chips = "".join(
            f"<span class='chip'><span class='em'>{GENRE_EMOJI.get(g, '🎬')}</span>{html.escape(g)}</span>"
            for g in genre_names
        ) or "<span class='chip'>-</span>"
        overview = html.escape(data.get("overview") or "No overview available.")

        backdrop = data.get("backdrop_url")
        if backdrop:
            bg = (
                "background-image: linear-gradient(90deg, rgba(19,17,31,0.97) 28%, "
                f"rgba(19,17,31,0.55) 100%), url('{html.escape(backdrop)}');"
            )
        else:
            bg = "background: var(--surface);"

        st.markdown(
            f"<div class='hero' style=\"{bg}\">"
            f"<h2>{title_txt}</h2>"
            f"<div><span class='chip date'><span class='em'>📅</span>{release}</span>{genre_chips}</div>"
            f"<h4 style='margin-top:18px'><span class='ico'>📖</span>Story</h4>"
            f"<p>{overview}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown("<h3><span class='ico'>✨</span>You might also like</h3>", unsafe_allow_html=True)

    # Recommendations (TF-IDF + Genre) via your bundle endpoint
    title = (data.get("title") or "").strip()
    if title:
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": title, "tfidf_top_n": 12, "genre_limit": 12},
        )
        bundle = bundle if isinstance(bundle, dict) else {}

        tfidf_cards = to_cards_from_tfidf_items(bundle.get("tfidf_recommendations"))
        genre_cards = to_cards_from_tfidf_items(bundle.get("genre_recommendations"))

        # Genre fallback endpoint if the bundle had no genre picks
        err3 = None
        if not genre_cards:
            genre_only, err3 = api_get_json(
                "/recommend/genre", params={"tmdb_id": tmdb_id, "limit": 18}
            )
            if isinstance(genre_only, list):
                genre_cards = to_cards_from_tfidf_items(genre_only)

        tab_tfidf, tab_genre = st.tabs(
            ["🔎 Similar Movies (TF-IDF)", "🎭 More Like This (Genre)"]
        )
        with tab_tfidf:
            if tfidf_cards:
                poster_grid(tfidf_cards, cols=grid_cols, key_prefix="details_tfidf")
            else:
                reason = f" ({err2})" if err2 else ""
                st.info(
                    "No similar-movie matches for this title yet. "
                    f"Check out the Genre tab for more picks.{reason}"
                )
        with tab_genre:
            if genre_cards:
                poster_grid(genre_cards, cols=grid_cols, key_prefix="details_genre")
            else:
                st.warning("No recommendations available right now.")
    else:
        st.warning("No title available to compute recommendations.")