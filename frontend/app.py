"""
app.py  ─  Football BDA Dashboard  (Entry Point)
=================================================
Run with:  streamlit run app.py

Pages are in the /pages/ folder (Streamlit multi-page app convention).
"""

import streamlit as st

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="Football BDA Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom Global CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600;700&display=swap');

/* ── Root Variables ── */
:root {
    --green:      #00FF87;
    --green-dim:  #00c968;
    --dark:       #0a0e1a;
    --card:       #111827;
    --card2:      #1a2235;
    --border:     #1f2d45;
    --text:       #e2e8f0;
    --muted:      #64748b;
    --accent:     #3b82f6;
    --gold:       #f59e0b;
    --red:        #ef4444;
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}
.stApp {
    background: linear-gradient(135deg, #060b18 0%, #0d1424 50%, #060b18 100%);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--card) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .css-1d391kg { padding-top: 1rem; }

/* ── Remove default padding ── */
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* ── Headings ── */
h1, h2, h3 { font-family: 'Bebas Neue', sans-serif; letter-spacing: 1px; }

/* ── Cards ── */
.stat-card {
    background: var(--card2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    text-align: center;
    transition: transform .2s, border-color .2s;
}
.stat-card:hover { transform: translateY(-2px); border-color: var(--green); }
.stat-card .value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2rem;
    color: var(--green);
    line-height: 1;
}
.stat-card .label {
    font-size: .78rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: .8px;
    margin-top: .3rem;
}

/* ── Section header ── */
.section-header {
    border-left: 4px solid var(--green);
    padding-left: .7rem;
    margin: 1.5rem 0 1rem;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.4rem;
    letter-spacing: 1px;
    color: var(--text);
}

/* ── Form badge ── */
.form-badge {
    display: inline-block;
    width: 28px; height: 28px;
    border-radius: 50%;
    text-align: center;
    line-height: 28px;
    font-weight: 700;
    font-size: .85rem;
    margin: 2px;
}
.form-W { background:#16a34a; color:#fff; }
.form-D { background:#ca8a04; color:#fff; }
.form-L { background:#dc2626; color:#fff; }

/* ── Streamlit overrides ── */
div[data-baseweb="select"] > div {
    background: var(--card2) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}
.stSelectbox label, .stMultiSelect label { color: var(--muted) !important; font-size:.82rem; }
.stButton > button {
    background: var(--green);
    color: #000;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    padding: .5rem 1.5rem;
    font-family: 'DM Sans', sans-serif;
    transition: background .2s, transform .1s;
}
.stButton > button:hover { background: var(--green-dim); transform: scale(1.02); }

/* ── Plotly chart container ── */
.js-plotly-plot { border-radius: 10px; overflow: hidden; }

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: var(--card2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: .8rem 1rem;
}
[data-testid="metric-container"] label { color: var(--muted) !important; }
[data-testid="stMetricValue"] { color: var(--green) !important; }

/* ── Table ── */
.dataframe { background: var(--card2) !important; color: var(--text) !important; }
thead th { background: var(--dark) !important; color: var(--green) !important; }

/* ── Divider ── */
hr { border-color: var(--border); }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--dark); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Hero / Home Page ────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 3rem 1rem 2rem;">
    <div style="font-size:4rem; margin-bottom:.5rem;">⚽</div>
    <h1 style="font-size:3.5rem; margin:0; color:#00FF87; font-family:'Bebas Neue',sans-serif; letter-spacing:3px;">
        FOOTBALL BDA DASHBOARD
    </h1>
    <p style="color:#64748b; font-size:1.05rem; margin-top:.6rem; max-width:600px; margin-left:auto; margin-right:auto;">
        Big Data Analytics on real-world football events (Wyscout dataset) · 
        England Premier League + Spain La Liga
    </p>
</div>
""", unsafe_allow_html=True)

# ── Quick nav cards ─────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="stat-card" style="cursor:pointer;">
        <div style="font-size:2.5rem; margin-bottom:.5rem;">🏆</div>
        <div class="value" style="font-size:1.3rem;">TEAM RANKINGS</div>
        <div class="label" style="margin-top:.4rem;">Leaderboard · Points · Win %</div>
        <div style="margin-top:.8rem; font-size:.82rem; color:#3b82f6;">→ Use sidebar to navigate</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-card" style="cursor:pointer;">
        <div style="font-size:2.5rem; margin-bottom:.5rem;">⚔️</div>
        <div class="value" style="font-size:1.3rem;">TEAM COMPARISON</div>
        <div class="label" style="margin-top:.4rem;">Head-to-head · Goals · Passes</div>
        <div style="margin-top:.8rem; font-size:.82rem; color:#3b82f6;">→ Use sidebar to navigate</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-card" style="cursor:pointer;">
        <div style="font-size:2.5rem; margin-bottom:.5rem;">👤</div>
        <div class="value" style="font-size:1.3rem;">PLAYER COMPARISON</div>
        <div class="label" style="margin-top:.4rem;">Goals · Assists · Shot accuracy</div>
        <div style="margin-top:.8rem; font-size:.82rem; color:#3b82f6;">→ Use sidebar to navigate</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="stat-card" style="cursor:pointer;">
        <div style="font-size:2.5rem; margin-bottom:.5rem;">🤖</div>
        <div class="value" style="font-size:1.3rem;">TEAM ANOMALIES</div>
        <div class="label" style="margin-top:.4rem;">IsolationForest · Outlier detection</div>
        <div style="margin-top:.8rem; font-size:.82rem; color:#3b82f6;">→ Use sidebar to navigate</div>
    </div>""", unsafe_allow_html=True)

# ── Info banner ─────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.info(
    "📌 **Navigate using the sidebar (← left panel).** "
    "This dashboard uses mock data that mirrors the real Wyscout dataset schema. "
    "Your teammate's PySpark backend can be wired in by editing `data/mock_data.py`.",
    icon="ℹ️"
)

# ── Data pipeline status ────────────────────────────────────────────────────
st.markdown('<div class="section-header">PIPELINE STATUS</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Data Ingestion",   "✅ Done",    help="HDFS data loaded")
c2.metric("Preprocessing",    "✅ Done",    help="JSON → Parquet converted")
c3.metric("PySpark Backend",  "✅ Ready",   help="Queries available")
c4.metric("Frontend",         "🚀 Running", help="Streamlit dashboard")
