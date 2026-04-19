"""
pages/1_🏆_Team_Rankings.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from api_connector import get_all_team_stats, get_team_form, get_teams_for_league

st.set_page_config(page_title="Team Rankings · Football BDA", page_icon="🏆", layout="wide")

# ── Inject shared CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600;700&display=swap');
:root{--green:#00FF87;--dark:#0a0e1a;--card:#111827;--card2:#1a2235;--border:#1f2d45;--text:#e2e8f0;--muted:#64748b;}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--text);}
.stApp{background:linear-gradient(135deg,#060b18 0%,#0d1424 50%,#060b18 100%);}
[data-testid="stSidebar"]{background:var(--card)!important;border-right:1px solid var(--border);}
h1,h2,h3{font-family:'Bebas Neue',sans-serif;letter-spacing:1px;}
.block-container{padding-top:1.5rem;}
.section-header{border-left:4px solid var(--green);padding-left:.7rem;margin:1.5rem 0 1rem;font-family:'Bebas Neue',sans-serif;font-size:1.4rem;letter-spacing:1px;}
.stat-card{background:var(--card2);border:1px solid var(--border);border-radius:12px;padding:1.2rem 1.4rem;text-align:center;}
.stat-card .value{font-family:'Bebas Neue',sans-serif;font-size:2rem;color:var(--green);line-height:1;}
.stat-card .label{font-size:.78rem;color:var(--muted);text-transform:uppercase;letter-spacing:.8px;margin-top:.3rem;}
[data-testid="metric-container"]{background:var(--card2);border:1px solid var(--border);border-radius:10px;padding:.8rem 1rem;}
[data-testid="stMetricValue"]{color:var(--green)!important;}
.form-badge{display:inline-block;width:26px;height:26px;border-radius:50%;text-align:center;line-height:26px;font-weight:700;font-size:.8rem;margin:2px;}
.form-W{background:#16a34a;color:#fff;} .form-D{background:#ca8a04;color:#fff;} .form-L{background:#dc2626;color:#fff;}
</style>
""", unsafe_allow_html=True)

# ── Page Header ──────────────────────────────────────────────────────────────
st.markdown("""
<h1 style="font-size:2.8rem;color:#00FF87;margin-bottom:0;">🏆 TEAM RANKINGS</h1>
<p style="color:#64748b;margin-top:.3rem;">Leaderboard based on points, win %, goals scored & recent form</p>
""", unsafe_allow_html=True)

# ── Filters ──────────────────────────────────────────────────────────────────
col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
with col_f1:
    league_filter = st.selectbox(
        "League",
        ["All Leagues", "England (Premier League)", "Spain (La Liga)"]
    )
with col_f2:
    sort_by = st.selectbox(
        "Sort by",
        ["points", "win_pct", "goals_scored", "goal_difference", "pass_accuracy"]
    )
with col_f3:
    show_n = st.selectbox("Show top", [8, 10, 16], index=0)

# ── Load & Filter Data ────────────────────────────────────────────────────────
df = get_all_team_stats()

if league_filter == "England (Premier League)":
    from api_connector import TEAMS_ENGLAND
    df = df[df["team_name"].isin(TEAMS_ENGLAND)]
elif league_filter == "Spain (La Liga)":
    from api_connector import TEAMS_SPAIN
    df = df[df["team_name"].isin(TEAMS_SPAIN)]

df = df.sort_values(sort_by, ascending=False).head(show_n).reset_index(drop=True)
df.index += 1
df.index.name = "Rank"

# ── Summary KPIs ──────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
top_team = df.iloc[0]
k1.metric("🥇 Top Team",     top_team["team_name"])
k2.metric("⚽ Most Goals",   int(df["goals_scored"].max()))
k3.metric("📊 Avg Win %",    f"{df['win_pct'].mean():.1f}%")
k4.metric("🎯 Avg Pass Acc", f"{df['pass_accuracy'].mean():.1f}%")

st.markdown('<div class="section-header">LEADERBOARD</div>', unsafe_allow_html=True)

# ── Leaderboard Table ─────────────────────────────────────────────────────────
PLOTLY_DARK = "#0d1424"

def form_html(team):
    form = get_team_form(team)
    badges = "".join(
        f'<span class="form-badge form-{r}">{r}</span>' for r in form
    )
    return badges

display_cols = ["team_name","matches_played","wins","draws","losses",
                "goals_scored","goals_against","goal_difference","points","win_pct","pass_accuracy"]
rename = {
    "team_name":"Team","matches_played":"MP","wins":"W","draws":"D",
    "losses":"L","goals_scored":"GF","goals_against":"GA",
    "goal_difference":"GD","points":"Pts","win_pct":"Win%","pass_accuracy":"Pass Acc%"
}
table_df = df[display_cols].rename(columns=rename).reset_index(drop=True)
table_df.insert(0, "#", range(1, len(table_df) + 1))

# Style dataframe
def highlight_top3(row):
    rank = row["#"]
    if rank == 1: return ["background-color:#1a3a1e; color:#00FF87; font-weight:700"]*len(row)
    if rank == 2: return ["background-color:#1c2a1a"]*len(row)
    if rank == 3: return ["background-color:#1a241c"]*len(row)
    return [""]*len(row)

styled = table_df.style.apply(highlight_top3, axis=1)\
    .format({"Win%":"{:.1f}%", "Pass Acc%":"{:.1f}%"})\
    .set_properties(**{"text-align":"center"})\
    .set_table_styles([
        {"selector":"th","props":[("background","#060b18"),("color","#00FF87"),
                                  ("font-family","'Bebas Neue',sans-serif"),
                                  ("letter-spacing","1px"),("text-align","center")]},
        {"selector":"td","props":[("color","#e2e8f0"),("border-color","#1f2d45")]},
    ])

st.dataframe(styled, width="stretch", height=420)

# ── Form Column (recent 5) ────────────────────────────────────────────────────
st.markdown('<div class="section-header">RECENT FORM (LAST 5 MATCHES)</div>', unsafe_allow_html=True)
form_html_list = []
for _, row in df.iterrows():
    badges = form_html(row["team_name"])
    form_html_list.append(f"""
    <div style="display:flex;align-items:center;gap:12px;padding:.5rem .8rem;
                background:#111827;border:1px solid #1f2d45;border-radius:8px;margin-bottom:.4rem;">
        <span style="width:180px;font-weight:600;color:#e2e8f0;">{row['team_name']}</span>
        <span style="color:#64748b;font-size:.78rem;width:50px;">Pts: <b style="color:#00FF87">{row['points']}</b></span>
        {badges}
    </div>
    """)
st.markdown("".join(form_html_list), unsafe_allow_html=True)

# ── Bar Chart: Points ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">POINTS COMPARISON</div>', unsafe_allow_html=True)

fig_pts = px.bar(
    df.reset_index(), x="team_name", y="points",
    color="points",
    color_continuous_scale=[[0,"#1f2d45"],[0.5,"#00c968"],[1,"#00FF87"]],
    labels={"team_name":"Team","points":"Points"},
    text="points",
)
fig_pts.update_traces(textposition="outside", textfont_color="#e2e8f0")
fig_pts.update_layout(
    plot_bgcolor=PLOTLY_DARK, paper_bgcolor="rgba(0,0,0,0)",
    font_color="#e2e8f0", font_family="DM Sans",
    xaxis=dict(tickangle=-30, gridcolor="#1f2d45"),
    yaxis=dict(gridcolor="#1f2d45"),
    coloraxis_showscale=False,
    margin=dict(t=30, b=10),
    height=370,
)
st.plotly_chart(fig_pts, width="stretch")

# ── Scatter: Goals vs Win % ───────────────────────────────────────────────────
st.markdown('<div class="section-header">GOALS SCORED vs WIN %</div>', unsafe_allow_html=True)

fig_scat = px.scatter(
    df.reset_index(), x="goals_scored", y="win_pct",
    size="points", color="points",
    hover_name="team_name",
    text="team_name",
    color_continuous_scale=[[0,"#1f2d45"],[1,"#00FF87"]],
    labels={"goals_scored":"Goals Scored","win_pct":"Win %","points":"Points"},
)
fig_scat.update_traces(textposition="top center", textfont_size=10, textfont_color="#e2e8f0")
fig_scat.update_layout(
    plot_bgcolor=PLOTLY_DARK, paper_bgcolor="rgba(0,0,0,0)",
    font_color="#e2e8f0", font_family="DM Sans",
    xaxis=dict(gridcolor="#1f2d45"),
    yaxis=dict(gridcolor="#1f2d45"),
    coloraxis_showscale=False,
    margin=dict(t=30, b=10),
    height=420,
)
st.plotly_chart(fig_scat, width="stretch")

# ── Backend note ──────────────────────────────────────────────────────────────
with st.expander("🔌 Backend Integration Note"):
    st.code("""
# In data/mock_data.py  →  replace get_all_team_stats() with:

def get_all_team_stats():
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.getOrCreate()
    df = spark.sql('''
        SELECT teamName,
               COUNT(DISTINCT matchId)                         AS matches_played,
               SUM(CASE WHEN eventName='Goal' THEN 1 END)     AS goals_scored,
               ...
        FROM events
        GROUP BY teamName
    ''').toPandas()
    return df
    """, language="python")
