import html
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "movie_recommender"

st.set_page_config(page_title="CineMatch | Movie Recommender", page_icon="🎬", layout="wide")

# ───────────────────────── Styling (palette from your Sketch design) ─────────────────────────
st.markdown("""
<style>
:root{--bg:#07060b;--panel:#0f0d18;--line:#221e30;--ink:#f6f2ea;--mute:#8c87a0;
      --lime:#d7ff3e;--violet:#7b5cff;--coral:#ff8a5b}
html,body,[data-testid="stAppViewContainer"],.stApp{background:var(--bg)!important;color:var(--ink)}
[data-testid="stAppViewContainer"]{
  background:
   radial-gradient(900px 500px at 15% -5%,rgba(123,92,255,.22),transparent 60%),
   radial-gradient(700px 500px at 95% 40%,rgba(215,255,62,.07),transparent 60%),var(--bg)!important}
[data-testid="stHeader"],footer,#MainMenu{display:none!important}
.block-container{max-width:1112px;padding-top:2rem;padding-bottom:6rem}
html{scroll-behavior:smooth}
*{cursor:none!important}                      /* custom cursor replaces the default one */
@media (hover:none){*{cursor:auto!important}}

/* header */
.nav{display:flex;justify-content:space-between;align-items:center;margin-bottom:5rem}
.brand{display:flex;align-items:center;gap:12px;font-weight:800;font-size:21px}
.logo{width:34px;height:34px;border-radius:9px;background:var(--lime);color:var(--bg);
      display:grid;place-items:center;font-weight:800;animation:pulse 3s ease-in-out infinite}
.pill{background:#14111e;border:1px solid var(--line);padding:9px 16px;border-radius:99px;
      font-size:12px;font-weight:600;letter-spacing:.08em}
.pill i{display:inline-block;width:5px;height:5px;border-radius:50%;background:var(--lime);margin-right:9px;
        animation:blink 1.4s infinite}
/* hero */
.kicker{color:var(--lime);font-size:11px;font-weight:700;letter-spacing:.16em;display:flex;gap:12px;align-items:center}
.kicker:before{content:"";width:28px;height:2px;background:var(--lime)}
.hero{font-size:clamp(48px,9vw,104px);font-weight:800;line-height:.98;letter-spacing:-.03em;margin:18px 0}
.hero span{display:inline-block;opacity:0;transform:translateY(40px);animation:rise .9s cubic-bezier(.2,.8,.2,1) forwards}
.hero .v{color:var(--violet)}
.hero span:nth-child(2){animation-delay:.12s}.hero span:nth-child(3){animation-delay:.24s}
.lede{max-width:560px;color:#a29cb8;font-size:16px;line-height:1.6;animation:rise 1s .4s both}
/* marquee */
.marq{overflow:hidden;border-block:1px solid var(--line);margin:3.5rem 0;padding:16px 0;
      mask-image:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent)}
.marq div{display:flex;gap:40px;width:max-content;animation:scroll 40s linear infinite;
          color:#c7c1d8;font-size:13px;font-weight:500;white-space:nowrap}
.marq b{color:var(--lime)}
.marq:hover div{animation-play-state:paused}
/* section labels */
.sec{font-size:11px;font-weight:700;letter-spacing:.16em;color:var(--violet);margin-top:2rem}
.sec.l{color:var(--lime)}
h2.t{font-size:clamp(26px,4vw,36px);font-weight:800;letter-spacing:-.02em;margin:.3rem 0 1.2rem}
/* tabs */
[data-baseweb="tab-list"]{gap:8px;border-bottom:1px solid var(--line)}
[data-baseweb="tab"]{background:transparent!important;color:var(--mute)!important;font-weight:600;padding:12px 18px}
[aria-selected="true"]{color:var(--lime)!important}
[data-baseweb="tab-highlight"]{background:var(--lime)!important;height:2px!important}
/* inputs / buttons */
[data-baseweb="select"]>div{background:#171325!important;border:1px solid var(--line)!important;border-radius:12px;
      transition:border-color .2s,box-shadow .2s}
[data-baseweb="select"]>div:focus-within,[data-baseweb="select"]>div:hover{border-color:var(--lime)!important;
      box-shadow:0 0 0 3px rgba(215,255,62,.12)}
.stButton>button{background:var(--lime);color:var(--bg);border:0;border-radius:12px;font-weight:700;
      padding:.7rem 1.6rem;transition:transform .2s,box-shadow .2s}
.stButton>button:hover{transform:translateY(-3px);box-shadow:0 12px 30px -8px rgba(215,255,62,.55);color:var(--bg)}
.stButton>button:active{transform:scale(.97)}
/* "Find Similar Movies" button (key="b1") - change --btn1 to any color you like */
.st-key-b1{--btn1:#7b5cff}
.st-key-b1 .stButton>button,.st-key-b1 button{background:var(--btn1);color:#fff}
.st-key-b1 button:hover{color:#fff;box-shadow:0 12px 30px -8px var(--btn1)}
.st-key-b1 button p{color:#fff}
/* results */
.res{background:#0b0912;border:1px solid var(--line);border-radius:14px;overflow:hidden;margin-top:1.2rem}
.rh,.rw{display:grid;grid-template-columns:40px 1fr 220px;gap:14px;align-items:center;padding:14px 18px}
.rh{background:#141121;font-size:10px;font-weight:700;letter-spacing:.14em;color:#6e6884}
.rw{border-top:1px solid var(--line);opacity:0;animation:rise .6s cubic-bezier(.2,.8,.2,1) forwards;transition:background .2s,padding-left .2s}
.rw:hover{background:#171325;padding-left:26px}
.rw .n{width:22px;height:22px;border-radius:6px;background:var(--line);color:var(--lime);font-size:11px;
       font-weight:700;display:grid;place-items:center}
.bar{height:5px;background:var(--line);border-radius:9px;overflow:hidden;flex:1}
.bar i{display:block;height:100%;width:0;border-radius:9px;background:var(--violet);
       animation:fill 1.1s cubic-bezier(.2,.8,.2,1) forwards;animation-delay:inherit}
.rw:first-of-type .bar i{background:var(--lime)}
.sc{display:flex;gap:10px;align-items:center;font-weight:700;font-size:13px;color:#c7c1d8}
.badge{display:inline-block;margin:.8rem 0 0;color:var(--lime);font-size:12px;font-weight:700;letter-spacing:.12em}
/* signals + steps (scroll-driven reveal) */
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin-top:1.4rem}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:20px;
      transition:transform .3s,border-color .3s}
.card:hover{transform:translateY(-6px) rotate(-.4deg);border-color:var(--c)}
.card h4{margin:34px 0 8px;font-size:17px;font-weight:800}.card p{margin:0;color:#a29cb8;font-size:13px}
.ech{position:relative;height:42px;width:144px}
.ech i{position:absolute;width:92px;height:26px;border-radius:5px;background:#1a1628;transition:transform .4s}
.ech i:nth-child(2){left:20px;top:8px;background:#2a2140}.ech i:nth-child(3){left:40px;top:16px;background:var(--c)}
.card:hover .ech i:nth-child(3){transform:translateX(18px)}
.step b{font-size:11px;letter-spacing:.14em;color:var(--c)}
.step h3{font-size:24px;font-weight:800;margin:.7rem 0 .4rem}
.reveal{animation:rise linear both;animation-timeline:view();animation-range:entry 0% entry 45%}
.closing{font-size:clamp(40px,7vw,72px);font-weight:800;line-height:1;letter-spacing:-.03em;margin:4rem 0 1rem}
.closing em{font-style:normal;color:var(--violet)}
.foot{color:#6e6884;font-size:12px;border-top:1px solid var(--line);padding-top:18px;margin-top:3rem}
/* injected by JS: cursor, ring, progress rail */
#cm-dot{position:fixed;z-index:9999;width:10px;height:10px;border-radius:50%;background:var(--lime);pointer-events:none;
        transform:translate(-50%,-50%);mix-blend-mode:difference}
#cm-ring{position:fixed;z-index:9998;width:64px;height:64px;border-radius:50%;background:rgba(215,255,62,.14);
        pointer-events:none;transform:translate(-50%,-50%);transition:width .25s,height .25s,background .25s}
#cm-ring.big{width:96px;height:96px;background:rgba(123,92,255,.25)}
#cm-rail{position:fixed;right:22px;top:20%;height:60%;width:2px;background:#22202e;z-index:999}
#cm-fill{width:100%;height:0;background:var(--lime)}
#cm-thumb{position:absolute;left:-5px;width:12px;height:12px;border-radius:50%;background:var(--lime);top:0;
          box-shadow:0 0 14px var(--lime)}
@keyframes rise{from{opacity:0;transform:translateY(34px)}to{opacity:1;transform:none}}
@keyframes fill{to{width:var(--w)}}
@keyframes scroll{to{transform:translateX(-50%)}}
@keyframes pulse{50%{box-shadow:0 0 0 10px rgba(215,255,62,0)}0%{box-shadow:0 0 0 0 rgba(215,255,62,.5)}}
@keyframes blink{50%{opacity:.2}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}.rw,.hero span{opacity:1!important}.bar i{width:var(--w)}}
</style>
""", unsafe_allow_html=True)

# Cursor follower + scroll progress rail (runs in the parent page)
components.html("""
<script>
const d=window.parent.document;
if(!d.getElementById('cm-dot')){
  d.body.insertAdjacentHTML('beforeend',
   '<div id="cm-dot"></div><div id="cm-ring"></div><div id="cm-rail"><div id="cm-fill"></div><div id="cm-thumb"></div></div>');
  const dot=d.getElementById('cm-dot'),ring=d.getElementById('cm-ring'),
        fill=d.getElementById('cm-fill'),thumb=d.getElementById('cm-thumb');
  let x=0,y=0,rx=0,ry=0;
  d.addEventListener('mousemove',e=>{x=e.clientX;y=e.clientY;dot.style.left=x+'px';dot.style.top=y+'px';
     ring.classList.toggle('big',!!e.target.closest('button,[data-baseweb="tab"],[data-baseweb="select"],.card'));});
  (function loop(){rx+=(x-rx)*.14;ry+=(y-ry)*.14;ring.style.left=rx+'px';ring.style.top=ry+'px';requestAnimationFrame(loop)})();
  const sc=d.querySelector('[data-testid="stMain"]')||d.querySelector('section.main')||d.scrollingElement;
  const upd=()=>{const p=sc.scrollTop/Math.max(1,sc.scrollHeight-sc.clientHeight);
     fill.style.height=(p*100)+'%';thumb.style.top=(p*100)+'%'};
  sc.addEventListener('scroll',upd);upd();
}
</script>""", height=0)

# ───────────────────────── Model (unchanged logic) ─────────────────────────
@st.cache_resource
def load_model():
    similarity = joblib.load(DATA_DIR / "item_similarity_df.pkl")
    train_matrix = joblib.load(DATA_DIR / "train_matrix.pkl")
    global_mean = joblib.load(DATA_DIR / "train_data.pkl")
    movies = pd.read_csv(DATA_DIR / "movie_info.csv")
    return similarity, train_matrix, global_mean, movies

try:
    item_similarity_df, train_matrix, global_mean, movie_info = load_model()
except FileNotFoundError:
    st.error("Model files not found. Place all four saved artifacts in the same folder as app.py.")
    st.stop()

movie_info["movie_id"] = movie_info["movie_id"].astype(int)
movie_titles = movie_info.drop_duplicates("movie_id").set_index("movie_id")["title"]


def find_similar_movies(movie_id, n=5):
    scores = item_similarity_df[movie_id].drop(movie_id).sort_values(ascending=False).head(n)
    result = pd.DataFrame({"movie_id": scores.index, "Similarity score": scores.values})
    result["Movie title"] = result["movie_id"].map(movie_titles)
    return result[["Movie title", "Similarity score"]]


def predict_rating(user_id, movie_id):
    if user_id not in train_matrix.index or movie_id not in item_similarity_df.index:
        return float(global_mean)
    user_ratings = train_matrix.loc[user_id].dropna()
    sims = item_similarity_df.loc[movie_id, user_ratings.index]
    sims = sims[sims > 0]
    if sims.empty:
        return float(global_mean)
    return float((sims * user_ratings.loc[sims.index]).sum() / sims.abs().sum())


def recommend_movies(user_id, n=10):
    if user_id not in train_matrix.index:
        return pd.DataFrame()
    watched = set(train_matrix.loc[user_id].dropna().index)
    unseen = [m for m in train_matrix.columns if m not in watched and m in item_similarity_df.index]
    preds = sorted(((int(m), predict_rating(user_id, m)) for m in unseen), key=lambda x: x[1], reverse=True)
    result = pd.DataFrame(preds[:n], columns=["movie_id", "Predicted rating"])
    result["Movie title"] = result["movie_id"].map(movie_titles)
    return result[["Movie title", "Predicted rating"]].reset_index(drop=True)


def results_html(df, col, max_val):
    """Animated result table: staggered rows + score bars that grow in."""
    rows = ""
    for i, (t, v) in enumerate(zip(df["Movie title"], df[col])):
        w = max(4, min(100, v / max_val * 100))
        rows += (f'<div class="rw" style="animation-delay:{i*.09:.2f}s">'
                 f'<div class="n">{i+1}</div><div>{html.escape(str(t))}</div>'
                 f'<div class="sc"><div class="bar"><i style="--w:{w:.0f}%"></i></div>{v:.3f}</div></div>')
    return (f'<div class="res"><div class="rh"><div></div><div>MOVIE</div>'
            f'<div>{col.upper()}</div></div>{rows}</div>')


# ───────────────────────── Page ─────────────────────────
st.markdown("""
<div class="nav"><div class="brand"><div class="logo">C</div>CineMatch</div>
<div class="pill"><i></i>GET STARTED</div></div>
<div class="kicker">RECOMMENDATION ENGINE</div>
<div class="hero"><span>Every film</span><br><span>echoes</span> <span class="v">another.</span></div>
<p class="lede">Explore movies with similar rating patterns or get recommendations based on a user's rating history.</p>
""", unsafe_allow_html=True)

ticker = "".join(f"<span><b>●</b> {html.escape(t)}</span>" for t in movie_titles.sample(min(14, len(movie_titles)), random_state=7))
st.markdown(f'<div class="marq"><div>{ticker}{ticker}</div></div>', unsafe_allow_html=True)

similar_tab, personal_tab = st.tabs(["Find Similar Movies", "For You"])

with similar_tab:
    st.markdown('<div class="sec">02 — LIVE PAIRING</div><h2 class="t">Pick a title, see the match.</h2>', unsafe_allow_html=True)
    available = movie_info.sort_values("title")
    title = st.selectbox("Choose a movie", available["title"].tolist(), key="similar_movie")
    if st.button("Find Similar Movies →", key="b1"):
        mid = int(available[available["title"] == title].iloc[0]["movie_id"])
        res = find_similar_movies(mid, 5)
        if res.empty:
            st.info("No similar movies were found.")
        else:
            st.markdown(f'<div class="badge">BECAUSE YOU SELECTED · {html.escape(title).upper()}</div>', unsafe_allow_html=True)
            st.markdown(results_html(res, "Similarity score", max(res["Similarity score"].max(), 1e-9)), unsafe_allow_html=True)

with personal_tab:
    st.markdown('<div class="sec l">YOUR LIST</div><h2 class="t">Taste has a fingerprint.</h2>', unsafe_allow_html=True)
    user = st.selectbox("Select a MovieLens user", sorted(int(u) for u in train_matrix.index), key="selected_user")
    st.caption("Choose an existing MovieLens user to see recommendations based on their recorded ratings.")
    if st.button("Recommend Movies →", key="b2"):
        res = recommend_movies(user, 10)
        if res.empty:
            st.info("No recommendations are available for this user.")
        else:
            st.markdown(results_html(res, "Predicted rating", 5.0), unsafe_allow_html=True)

st.markdown("""
<div class="sec l" style="margin-top:5rem">03 — WHAT WE READ</div>
<h2 class="t">Four signals, one fingerprint.</h2>
<div class="grid">
 <div class="card reveal" style="--c:#d7ff3e"><div class="ech"><i></i><i></i><i></i></div><h4>Rating pattern</h4><p>Where the curve bends, not just the average.</p></div>
 <div class="card reveal" style="--c:#9b7bff"><div class="ech"><i></i><i></i><i></i></div><h4>Similar taste</h4><p>Users who rated alike pull titles together.</p></div>
 <div class="card reveal" style="--c:#ff8a5b"><div class="ech"><i></i><i></i><i></i></div><h4>Positive links only</h4><p>Only movies with positive similarity vote.</p></div>
 <div class="card reveal" style="--c:#63e6d2"><div class="ech"><i></i><i></i><i></i></div><h4>Weighted score</h4><p>Closer movies count for more in the average.</p></div>
</div>
<div class="sec" style="margin-top:5rem">04 — THE SEQUENCE</div>
<h2 class="t">Three steps, one long take.</h2>
<div class="grid">
 <div class="step reveal" style="--c:#d7ff3e"><b>● STEP 01</b><h3>Pick a film</h3><p style="color:#a29cb8">Start from a favourite you already rewatch.</p></div>
 <div class="step reveal" style="--c:#9b7bff"><b>● STEP 02</b><h3>We read the vector</h3><p style="color:#a29cb8">Ratings become a comparable fingerprint.</p></div>
 <div class="step reveal" style="--c:#ff8a5b"><b>● STEP 03</b><h3>Echoes come back</h3><p style="color:#a29cb8">A ranked shortlist with a score you can argue with.</p></div>
</div>
<div class="closing">Find the next<br><em>favourite.</em></div>
<div class="foot">CINEMATCH · Movie Recommender · 2026</div>
""", unsafe_allow_html=True)
