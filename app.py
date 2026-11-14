import html
import requests
import streamlit as st
import streamlit.components.v1 as components
from urllib.parse import quote


# CONFIG

API_BASE = "https://cinematch-a-movie-recommendation-system.onrender.com" or "http://127.0.0.1:8000"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

# LOGO (inline SVG: gold reel ring + teal play triangle)
LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="{size}" height="{size}">
<defs>
<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffd978"/><stop offset="1" stop-color="#e9a62b"/></linearGradient>
<linearGradient id="t" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3be3cf"/><stop offset="1" stop-color="#12a897"/></linearGradient>
</defs>
<circle cx="32" cy="32" r="28" fill="#0b1020" stroke="url(#g)" stroke-width="4"/>
<circle cx="32" cy="12.5" r="4.2" fill="url(#g)"/>
<circle cx="50.5" cy="25.9" r="4.2" fill="url(#g)"/>
<circle cx="43.4" cy="47.6" r="4.2" fill="url(#g)"/>
<circle cx="20.6" cy="47.6" r="4.2" fill="url(#g)"/>
<circle cx="13.5" cy="25.9" r="4.2" fill="url(#g)"/>
<path d="M27 23 L27 41 L42 32 Z" fill="url(#t)"/>
</svg>"""

st.set_page_config(page_title="CineMatch · Movie Recommender", page_icon="🎬", layout="wide")

# Tab icon (custom SVG favicon, falls back to the emoji above if blocked)
_fav = "data:image/svg+xml;utf8," + quote(LOGO_SVG.format(size=64))
components.html(
    f"""<script>
    try {{
      const d = window.parent.document;
      d.querySelectorAll("link[rel*='icon']").forEach(e => e.remove());
      const l = d.createElement('link');
      l.rel = 'icon'; l.type = 'image/svg+xml'; l.href = "{_fav}";
      d.head.appendChild(l);
    }} catch (e) {{}}
    </script>""",
    height=0,
)


# STYLES (cinematic navy + gold/teal glow, glassmorphism)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --bg: #0b1020;
  --gold: #f6c453;
  --gold-2: #e9a62b;
  --teal: #19c3b1;
  --text: #e8ecf6;
  --muted: #94a0b8;
  --glass: rgba(255,255,255,0.05);
  --glass-border: rgba(255,255,255,0.10);
}

html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; color: var(--text); }

/* Background: navy base, gold glow top-left, teal glow bottom-right */
.stApp {
  background:
    radial-gradient(900px 600px at 0% 0%, rgba(246,196,83,0.20), transparent 60%),
    radial-gradient(900px 600px at 100% 100%, rgba(25,195,177,0.20), transparent 60%),
    #0b1020;
  background-attachment: fixed;
}
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1400px; }

/* Sidebar */
[data-testid="stSidebar"] {
  background: rgba(11,16,32,0.85);
  backdrop-filter: blur(14px);
  border-right: 1px solid var(--glass-border);
}

/* Header */
.brand { display:flex; align-items:center; gap:14px; margin-bottom: 4px; }
.brand-title { font-size: 2rem; font-weight: 800; letter-spacing: -0.5px;
  background: linear-gradient(90deg, var(--gold), #ffe9b0 45%, var(--teal));
  -webkit-background-clip: text; background-clip: text; color: transparent; }
.small-muted { color: var(--muted); font-size: 0.95rem; }
.section-title { font-size: 1.25rem; font-weight: 700; margin: 6px 0 10px 0; }
hr { border-color: var(--glass-border) !important; }

/* Inputs */
.stTextInput input, div[data-baseweb="select"] > div {
  background: var(--glass) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: 12px !important;
  color: var(--text) !important;
}
.stTextInput input:focus { border-color: var(--gold) !important; box-shadow: 0 0 0 2px rgba(246,196,83,0.25) !important; }

/* Buttons (gradient) */
.stButton > button {
  width: 100%;
  background: linear-gradient(135deg, var(--gold) 0%, var(--teal) 100%);
  color: #0b1020; font-weight: 700; border: none; border-radius: 10px;
  padding: 0.4rem 0.8rem; transition: transform .2s ease, box-shadow .2s ease, filter .2s ease;
}
.stButton > button:hover {
  transform: translateY(-2px); filter: brightness(1.08);
  box-shadow: 0 8px 22px rgba(25,195,177,0.35); color: #0b1020; border: none;
}
.stButton > button:active { transform: translateY(0); }

/* Movie cards (glass, hover lift + zoom) */
div[data-testid="stColumn"]:has(.pc), div[data-testid="column"]:has(.pc) {
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 10px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
}
div[data-testid="stColumn"]:has(.pc):hover, div[data-testid="column"]:has(.pc):hover {
  transform: translateY(-6px);
  border-color: rgba(246,196,83,0.45);
  box-shadow: 0 14px 34px rgba(0,0,0,0.45), 0 0 24px rgba(246,196,83,0.15);
}
.poster-wrap { position: relative; overflow: hidden; border-radius: 12px; aspect-ratio: 2/3; background: #141b33; margin-bottom: 8px; }
.poster-wrap img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform .45s ease; }
div[data-testid="stColumn"]:has(.pc):hover .poster-wrap img,
div[data-testid="column"]:has(.pc):hover .poster-wrap img { transform: scale(1.08); }
.no-poster { height: 100%; display:flex; align-items:center; justify-content:center; color: var(--muted); font-size: .85rem; }

.badge { position: absolute; top: 8px; padding: 3px 8px; border-radius: 999px; font-size: .72rem; font-weight: 700;
  backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); }
.badge.year { left: 8px; background: rgba(11,16,32,0.72); color: #fff; border: 1px solid rgba(255,255,255,0.18); }
.badge.rate { right: 8px; background: rgba(246,196,83,0.92); color: #0b1020; }

.movie-title { font-size: 0.9rem; font-weight: 600; line-height: 1.15rem; height: 2.3rem; overflow: hidden; margin-top: 8px; color: var(--text); }

/* Detail cards */
.card { border: 1px solid var(--glass-border); border-radius: 18px; padding: 18px; background: var(--glass);
  backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); box-shadow: 0 10px 30px rgba(0,0,0,0.35); }
.card h2 { margin-top: 0; }

/* Genre chips + meta */
.chips { display:flex; flex-wrap:wrap; gap:8px; margin: 10px 0 4px 0; }
.chip { padding: 5px 12px; border-radius: 999px; font-size: .8rem; font-weight: 600; color: var(--gold);
  background: rgba(246,196,83,0.10); border: 1px solid rgba(246,196,83,0.35); }
.meta-row { display:flex; flex-wrap:wrap; gap:14px; color: var(--muted); font-size: .92rem; margin-top: 6px; }
.meta-row b { color: var(--text); }
.overview { line-height: 1.7; color: #cfd6e6; }

/* Cinematic backdrop banner */
.hero { position: relative; border-radius: 20px; overflow: hidden; min-height: 280px; margin-bottom: 22px;
  background-size: cover; background-position: center 25%; border: 1px solid var(--glass-border);
  box-shadow: 0 18px 50px rgba(0,0,0,0.5); display:flex; align-items:flex-end; }
.hero::before { content:""; position:absolute; inset:0;
  background: linear-gradient(180deg, rgba(11,16,32,0.15) 0%, rgba(11,16,32,0.95) 100%),
              linear-gradient(90deg, rgba(246,196,83,0.18), transparent 50%, rgba(25,195,177,0.18)); }
.hero-inner { position: relative; padding: 24px 28px; }
.hero-title { font-size: 2.2rem; font-weight: 800; letter-spacing: -0.5px; text-shadow: 0 4px 20px rgba(0,0,0,0.6); }
.hero-sub { color: #d6dcec; font-size: .95rem; margin-top: 4px; }
.hero.plain { min-height: 150px; background: linear-gradient(135deg, rgba(246,196,83,0.18), rgba(25,195,177,0.18)); }
</style>
""",
    unsafe_allow_html=True,
)


# STATE + ROUTING (single-file pages)

if "view" not in st.session_state:
    st.session_state.view = "home"  # home | details
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None

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


def goto_home():
    st.session_state.view = "home"
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()


def goto_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()



# API HELPERS

@st.cache_data(ttl=30)  # short cache for autocomplete
def api_get_json(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}: {r.text[:300]}"
        return r.json(), None
    except Exception as e:
        return None, f"Request failed: {e}"


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

            # UI only: optional badges (shown only if the data has these fields)
            year = (m.get("release_date") or "")[:4]
            rating = m.get("vote_average")
            badges = ""
            if year:
                badges += f"<span class='badge year'>{html.escape(year)}</span>"
            try:
                if rating and float(rating) > 0:
                    badges += f"<span class='badge rate'>★ {float(rating):.1f}</span>"
            except (TypeError, ValueError):
                pass

            if poster:
                media = f"<img src='{html.escape(poster, quote=True)}' alt='poster'/>"
            else:
                media = "<div class='no-poster'>🖼️ No poster</div>"

            with colset[c]:
                st.markdown(
                    f"<span class='pc'></span><div class='poster-wrap'>{media}{badges}</div>",
                    unsafe_allow_html=True,
                )

                if st.button("▶ Open", key=f"{key_prefix}_{r}_{c}_{idx}_{tmdb_id}"):
                    if tmdb_id:
                        goto_details(tmdb_id)

                st.markdown(
                    f"<div class='movie-title'>{html.escape(str(title))}</div>",
                    unsafe_allow_html=True,
                )


def to_cards_from_tfidf_items(tfidf_items):
    cards = []
    for x in tfidf_items or []:
        tmdb = x.get("tmdb") or {}
        if tmdb.get("tmdb_id"):
            cards.append(
                {
                    "tmdb_id": tmdb["tmdb_id"],
                    "title": tmdb.get("title") or x.get("title") or "Untitled",
                    "poster_url": tmdb.get("poster_url"),
                    "release_date": tmdb.get("release_date", ""),
                    "vote_average": tmdb.get("vote_average"),
                }
            )
    return cards



# IMPORTANT: Robust TMDB search parsing
# Supports BOTH API shapes:
# 1) raw TMDB: {"results":[{id,title,poster_path,...}]}
# 2) list cards: [{tmdb_id,title,poster_url,...}]

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
                    "vote_average": m.get("vote_average"),
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
                    "vote_average": m.get("vote_average"),
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
        {
            "tmdb_id": x["tmdb_id"],
            "title": x["title"],
            "poster_url": x["poster_url"],
            "release_date": x.get("release_date", ""),
            "vote_average": x.get("vote_average"),
        }
        for x in final_list[:limit]
    ]
    return suggestions, cards



# SIDEBAR (clean)

with st.sidebar:
    st.markdown(
        f"<div class='brand'>{LOGO_SVG.format(size=38)}<div class='brand-title' style='font-size:1.4rem'>CineMatch</div></div>",
        unsafe_allow_html=True,
    )
    if st.button("🏠 Home"):
        goto_home()

    st.markdown("---")
    st.markdown("### Browse Collections")
    home_category = st.selectbox(
        "Category",
        ["trending", "popular", "top_rated", "now_playing", "upcoming"],
        index=0,
    )
    grid_cols = st.slider("Grid columns", 4, 8, 6)


# HEADER

st.markdown(
    f"<div class='brand'>{LOGO_SVG.format(size=52)}<div class='brand-title'>CineMatch</div></div>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div class='small-muted'>Search any title, explore the details, and discover films you'll love.</div>",
    unsafe_allow_html=True,
)
st.divider()


# VIEW: HOME

if st.session_state.view == "home":
    typed = st.text_input(
        "Search by movie title", placeholder="Try: avengers, batman, love..."
    )

    st.divider()

    # SEARCH MODE (Autocomplete + word-match results)
    if typed.strip():
        if len(typed.strip()) < 2:
            st.caption("Type at least 2 characters for suggestions.")
        else:
            data, err = api_get_json("/tmdb/search", params={"query": typed.strip()})

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

                st.markdown("<div class='section-title'>Search Results</div>", unsafe_allow_html=True)
                poster_grid(cards, cols=grid_cols, key_prefix="search_results")

        st.stop()

    # HOME FEED MODE
    st.markdown(
        f"<div class='section-title'>🔥 {home_category.replace('_',' ').title()}</div>",
        unsafe_allow_html=True,
    )

    home_cards, err = api_get_json(
        "/home", params={"category": home_category, "limit": 24}
    )
    if err or not home_cards:
        st.error(f"Home feed failed: {err or 'Unknown error'}")
        st.stop()

    poster_grid(home_cards, cols=grid_cols, key_prefix="home_feed")


# VIEW: DETAILS

elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.warning("No movie selected.")
        if st.button("← Back to Home"):
            goto_home()
        st.stop()

    # Top bar
    a, b = st.columns([3, 1])
    with a:
        st.markdown("<div class='section-title'>Movie Details</div>", unsafe_allow_html=True)
    with b:
        if st.button("← Back to Home"):
            goto_home()

    # Details (your FastAPI safe route)
    data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        st.stop()

    release = data.get("release_date") or "-"
    genre_names = [g["name"] for g in data.get("genres", [])]
    safe_title = html.escape(data.get("title", ""))

    # Cinematic backdrop banner
    if data.get("backdrop_url"):
        st.markdown(
            f"<div class='hero' style=\"background-image:url('{html.escape(data['backdrop_url'], quote=True)}')\">"
            f"<div class='hero-inner'><div class='hero-title'>{safe_title}</div>"
            f"<div class='hero-sub'>{html.escape(release)}</div></div></div>",
            unsafe_allow_html=True,
        )

    # Layout: Poster LEFT, Details RIGHT
    left, right = st.columns([1, 2.4], gap="large")

    with left:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        if data.get("poster_url"):
            st.image(data["poster_url"], use_container_width=True)
        else:
            st.write("🖼️ No poster")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        chips = "".join(f"<span class='chip'>{html.escape(g)}</span>" for g in genre_names)
        rating_html = ""
        try:
            if data.get("vote_average") and float(data["vote_average"]) > 0:
                rating_html = f"<span>⭐ <b>{float(data['vote_average']):.1f}</b> / 10</span>"
        except (TypeError, ValueError):
            pass
        overview = html.escape(data.get("overview") or "No overview available.")

        st.markdown(
            f"<div class='card'>"
            f"<h2>{safe_title}</h2>"
            f"<div class='chips'>{chips or '<span class=\"small-muted\">No genres listed</span>'}</div>"
            f"<div class='meta-row'><span>📅 Release: <b>{html.escape(release)}</b></span>{rating_html}</div>"
            f"<hr/>"
            f"<div class='section-title'>Overview</div>"
            f"<div class='overview'>{overview}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown("<div class='section-title'>✨ Recommended For You</div>", unsafe_allow_html=True)

    # Recommendations (TF-IDF + Genre) via your bundle endpoint
    title = (data.get("title") or "").strip()
    if title:
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": title, "tfidf_top_n": 12, "genre_limit": 12},
        )

        if not err2 and bundle:
            st.markdown("#### 🔎 Similar Movies")
            poster_grid(
                to_cards_from_tfidf_items(bundle.get("tfidf_recommendations")),
                cols=grid_cols,
                key_prefix="details_tfidf",
            )

            st.markdown("#### 🎭 More Like This")
            poster_grid(
                bundle.get("genre_recommendations", []),
                cols=grid_cols,
                key_prefix="details_genre",
            )
        else:
            st.info("Showing Genre recommendations (fallback).")
            genre_only, err3 = api_get_json(
                "/recommend/genre", params={"tmdb_id": tmdb_id, "limit": 18}
            )
            if not err3 and genre_only:
                poster_grid(
                    genre_only, cols=grid_cols, key_prefix="details_genre_fallback"
                )
            else:
                st.warning("No recommendations available right now.")
    else:
        st.warning("No title available to compute recommendations.")