"""
pages/3_👤_Player_Comparison.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from api_connector import get_player_stats, ALL_PLAYERS, PLAYERS, ALL_TEAMS

st.set_page_config(page_title="Player Comparison · Football BDA", page_icon="👤", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600;700&display=swap');
:root{--green:#00FF87;--dark:#0a0e1a;--card:#111827;--card2:#1a2235;--border:#1f2d45;--text:#e2e8f0;--muted:#64748b;--purple:#a855f7;--teal:#14b8a6;}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--text);}
.stApp{background:linear-gradient(135deg,#060b18 0%,#0d1424 50%,#060b18 100%);}
[data-testid="stSidebar"]{background:var(--card)!important;border-right:1px solid var(--border);}
h1,h2,h3{font-family:'Bebas Neue',sans-serif;letter-spacing:1px;}
.block-container{padding-top:1.5rem;}
.section-header{border-left:4px solid var(--green);padding-left:.7rem;margin:1.5rem 0 1rem;font-family:'Bebas Neue',sans-serif;font-size:1.4rem;letter-spacing:1px;}
.player-card{border-radius:12px;padding:1.2rem;text-align:center;position:relative;overflow:hidden;}
.player-a{background:linear-gradient(135deg,#1e0a3c,#3b0764);border:2px solid #a855f7;}
.player-b{background:linear-gradient(135deg,#001a1a,#003333);border:2px solid #14b8a6;}
.stat-pill{display:inline-block;background:#0d1424;border:1px solid #1f2d45;border-radius:20px;padding:.3rem .8rem;font-size:.82rem;margin:.2rem;}
.stButton>button{background:#00FF87;color:#000;font-weight:700;border:none;border-radius:8px;padding:.5rem 1.5rem;}
[data-testid="metric-container"]{background:#1a2235;border:1px solid #1f2d45;border-radius:10px;padding:.8rem 1rem;}
[data-testid="stMetricValue"]{color:#00FF87!important;}
</style>
""", unsafe_allow_html=True)

PLOTLY_DARK = "#0d1424"
PURPLE = "#a855f7"
TEAL = "#14b8a6"

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style="font-size:2.8rem;color:#00FF87;margin-bottom:0;">👤 PLAYER COMPARISON</h1>
<p style="color:#64748b;margin-top:.3rem;">Compare two players head-to-head across all performance metrics</p>
""", unsafe_allow_html=True)

# ── Player Selection ──────────────────────────────────────────────────────────
pc1, pc2, pc3 = st.columns([5, 1, 5])

with pc1:
    team_a = st.selectbox("Team (Player A)", ["All Teams"] + ALL_TEAMS, key="pta")
    pool_a = ALL_PLAYERS if team_a == "All Teams" else PLAYERS.get(team_a, ALL_PLAYERS)
    player_a = st.selectbox("🟣 Player A", pool_a, key="pa")

with pc2:
    st.markdown("<br><br><div style='text-align:center;font-family:\"Bebas Neue\",sans-serif;font-size:1.2rem;color:#64748b;padding-top:1.5rem;'>VS</div>", unsafe_allow_html=True)

with pc3:
    team_b = st.selectbox("Team (Player B)", ["All Teams"] + ALL_TEAMS, index=9, key="ptb")
    pool_b = ALL_PLAYERS if team_b == "All Teams" else PLAYERS.get(team_b, ALL_PLAYERS)
    player_b = st.selectbox("🔵 Player B", pool_b, index=min(1, len(pool_b)-1), key="pb")

st.markdown("<br>", unsafe_allow_html=True)

if player_a and player_b:
    pa = get_player_stats(player_a)
    pb = get_player_stats(player_b)

    # ── Player Cards ──────────────────────────────────────────────────────────
    ca, cx, cb = st.columns([5, 1, 5])
    with ca:
        st.markdown(f"""
        <div class="player-card player-a">
            <div style="font-size:3rem;margin-bottom:.3rem;">🟣</div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:1.7rem;color:#d8b4fe;letter-spacing:1px;">{player_a}</div>
            <div style="color:#9333ea;font-size:.9rem;margin:.3rem 0;">{pa['team_name']}</div>
            <div>
                <span class="stat-pill">⚽ {pa['goals']} Goals</span>
                <span class="stat-pill">🅰️ {pa['assists']} Assists</span>
                <span class="stat-pill">📅 {pa['matches_played']} Matches</span>
            </div>
        </div>""", unsafe_allow_html=True)
    with cx:
        st.markdown("<div style='text-align:center;padding-top:3rem;font-family:\"Bebas Neue\",sans-serif;font-size:1.3rem;color:#64748b;'>VS</div>", unsafe_allow_html=True)
    with cb:
        st.markdown(f"""
        <div class="player-card player-b">
            <div style="font-size:3rem;margin-bottom:.3rem;">🔵</div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:1.7rem;color:#99f6e4;letter-spacing:1px;">{player_b}</div>
            <div style="color:#0d9488;font-size:.9rem;margin:.3rem 0;">{pb['team_name']}</div>
            <div>
                <span class="stat-pill">⚽ {pb['goals']} Goals</span>
                <span class="stat-pill">🅰️ {pb['assists']} Assists</span>
                <span class="stat-pill">📅 {pb['matches_played']} Matches</span>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── KPI Row ───────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">KEY METRICS</div>', unsafe_allow_html=True)

    kpis = [
        ("⚽ Goals",        pa["goals"],           pb["goals"]),
        ("🅰️ Assists",      pa["assists"],          pb["assists"]),
        ("🎯 Shot Acc%",    pa["shot_accuracy"],    pb["shot_accuracy"]),
        ("📊 Pass Acc%",    pa["pass_accuracy"],    pb["pass_accuracy"]),
        ("🏃 Dribble%",     pa["dribble_success_pct"], pb["dribble_success_pct"]),
        ("⏱ Goals/90",     pa["goals_per_90"],     pb["goals_per_90"]),
    ]
    cols = st.columns(len(kpis))
    for col, (label, va, vb) in zip(cols, kpis):
        color_a = "#a855f7"; color_b = "#14b8a6"
        if va > vb:   color_a = "#00FF87"
        elif vb > va: color_b = "#00FF87"
        col.markdown(f"""
        <div style="background:#111827;border:1px solid #1f2d45;border-radius:10px;padding:.8rem;text-align:center;">
            <div style="font-size:.7rem;color:#64748b;margin-bottom:.3rem;">{label}</div>
            <div style="display:flex;justify-content:center;align-items:center;gap:.5rem;">
                <span style="font-family:'Bebas Neue',sans-serif;font-size:1.5rem;color:{color_a};">{va}</span>
                <span style="color:#1f2d45;">|</span>
                <span style="font-family:'Bebas Neue',sans-serif;font-size:1.5rem;color:{color_b};">{vb}</span>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Detailed Comparison Bars ───────────────────────────────────────────────
    st.markdown('<div class="section-header">DETAILED STATS BREAKDOWN</div>', unsafe_allow_html=True)

    metrics = [
        ("Goals",               "goals",                50),
        ("Assists",             "assists",              30),
        ("Total Passes",        "total_passes",         2500),
        ("Pass Accuracy %",     "pass_accuracy",        100),
        ("Shots",               "shots",                120),
        ("Shots on Target",     "shots_on_target",      80),
        ("Shot Accuracy %",     "shot_accuracy",        100),
        ("Dribbles",            "dribbles_attempted",   150),
        ("Dribble Success %",   "dribble_success_pct",  100),
        ("Tackles",             "tackles",              100),
        ("Goals per 90",        "goals_per_90",         1),
        ("Assists per 90",      "assists_per_90",       0.7),
    ]

    rows = []
    for label, key, max_val in metrics:
        va = pa[key]; vb = pb[key]
        pct_a = min(va / max(max_val, 0.01) * 100, 100)
        pct_b = min(vb / max(max_val, 0.01) * 100, 100)
        w_a = "font-weight:700;color:#00FF87;" if va > vb else ""
        w_b = "font-weight:700;color:#00FF87;" if vb > va else ""
        rows.append(f"""
        <div style="background:#111827;border:1px solid #1f2d45;border-radius:8px;padding:.75rem 1.2rem;margin:.35rem 0;">
            <div style="display:grid;grid-template-columns:1fr 170px 1fr;gap:.8rem;align-items:center;">
                <div style="text-align:right;">
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:1.25rem;color:#a855f7;{w_a}">{va}</div>
                    <div style="height:7px;background:#1f2d45;border-radius:4px;overflow:hidden;margin-top:3px;">
                        <div style="height:100%;width:{pct_a}%;background:linear-gradient(90deg,#7e22ce,#a855f7);border-radius:4px;float:right;"></div>
                    </div>
                </div>
                <div style="text-align:center;font-size:.78rem;color:#64748b;text-transform:uppercase;letter-spacing:.7px;">{label}</div>
                <div style="text-align:left;">
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:1.25rem;color:#14b8a6;{w_b}">{vb}</div>
                    <div style="height:7px;background:#1f2d45;border-radius:4px;overflow:hidden;margin-top:3px;">
                        <div style="height:100%;width:{pct_b}%;background:linear-gradient(90deg,#0f766e,#14b8a6);border-radius:4px;"></div>
                    </div>
                </div>
            </div>
        </div>""")
    st.markdown("".join(rows), unsafe_allow_html=True)

    # ── Radar ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">PERFORMANCE RADAR</div>', unsafe_allow_html=True)

    radar_cats = ["Goals","Assists","Pass Acc","Shot Acc","Dribble%","Tackles"]

    def norm(a, b):
        mx = max(a, b, 0.01)
        return round(a/mx*100,1), round(b/mx*100,1)

    pairs = [
        norm(pa["goals"],               pb["goals"]),
        norm(pa["assists"],             pb["assists"]),
        norm(pa["pass_accuracy"],       pb["pass_accuracy"]),
        norm(pa["shot_accuracy"],       pb["shot_accuracy"]),
        norm(pa["dribble_success_pct"], pb["dribble_success_pct"]),
        norm(pa["tackles"],             pb["tackles"]),
    ]
    va_r = [p[0] for p in pairs]
    vb_r = [p[1] for p in pairs]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=va_r + [va_r[0]], theta=radar_cats + [radar_cats[0]],
        fill="toself", name=player_a,
        line=dict(color=PURPLE, width=2),
        fillcolor="rgba(168,85,247,0.15)"
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=vb_r + [vb_r[0]], theta=radar_cats + [radar_cats[0]],
        fill="toself", name=player_b,
        line=dict(color=TEAL, width=2),
        fillcolor="rgba(20,184,166,0.15)"
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0,110], gridcolor="#1f2d45", tickfont=dict(color="#64748b",size=9)),
            angularaxis=dict(gridcolor="#1f2d45", tickfont=dict(color="#e2e8f0",size=10))
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        height=430,
        margin=dict(t=30, b=30),
    )
    st.plotly_chart(fig_radar, width="stretch")

    # ── Goals + Assists Grouped Bar ────────────────────────────────────────────
    st.markdown('<div class="section-header">GOALS & ASSISTS BREAKDOWN</div>', unsafe_allow_html=True)
    fig_ga = go.Figure(data=[
        go.Bar(name="Goals",   x=[player_a, player_b],
               y=[pa["goals"],   pb["goals"]],   marker_color=["#a855f7","#14b8a6"],
               text=[pa["goals"],   pb["goals"]],   textposition="outside"),
        go.Bar(name="Assists", x=[player_a, player_b],
               y=[pa["assists"], pb["assists"]], marker_color=["#7c3aed","#0d9488"],
               text=[pa["assists"], pb["assists"]], textposition="outside"),
    ])
    fig_ga.update_layout(
        barmode="group",
        plot_bgcolor=PLOTLY_DARK, paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0", font_family="DM Sans",
        xaxis=dict(gridcolor="#1f2d45"),
        yaxis=dict(gridcolor="#1f2d45"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        height=340, margin=dict(t=20, b=10),
    )
    st.plotly_chart(fig_ga, width="stretch")

    # ── Per-90 Comparison ─────────────────────────────────────────────────────
    st.markdown('<div class="section-header">PER 90 MINUTES</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        fig_p90a = go.Figure(go.Indicator(
            mode="gauge+number", value=pa["goals_per_90"],
            title={"text": f"{player_a}<br><span style='font-size:.8rem;color:#64748b'>Goals per 90</span>"},
            number={"font":{"color":PURPLE}},
            gauge={"axis":{"range":[0,1]},"bar":{"color":PURPLE},
                   "bgcolor":"#1a2235","bordercolor":"#1f2d45",
                   "steps":[{"range":[0,0.5],"color":"#1f2d45"},{"range":[0.5,1],"color":"#2d1f45"}]}
        ))
        fig_p90a.update_layout(paper_bgcolor="rgba(0,0,0,0)",font_color="#e2e8f0",height=260,margin=dict(t=40,b=10))
        st.plotly_chart(fig_p90a, width="stretch")
    with c2:
        fig_p90b = go.Figure(go.Indicator(
            mode="gauge+number", value=pb["goals_per_90"],
            title={"text": f"{player_b}<br><span style='font-size:.8rem;color:#64748b'>Goals per 90</span>"},
            number={"font":{"color":TEAL}},
            gauge={"axis":{"range":[0,1]},"bar":{"color":TEAL},
                   "bgcolor":"#1a2235","bordercolor":"#1f2d45",
                   "steps":[{"range":[0,0.5],"color":"#1f2d45"},{"range":[0.5,1],"color":"#0d2525"}]}
        ))
        fig_p90b.update_layout(paper_bgcolor="rgba(0,0,0,0)",font_color="#e2e8f0",height=260,margin=dict(t=40,b=10))
        st.plotly_chart(fig_p90b, width="stretch")

    with st.expander("🔌 Backend Integration Note"):
        st.code("""
# Replace get_player_stats() in data/mock_data.py:

def get_player_stats(player_name: str) -> dict:
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.getOrCreate()
    df = spark.sql(f\"\"\"
        SELECT
            playerName,
            teamName,
            COUNT(DISTINCT matchId)                             AS matches_played,
            SUM(CASE WHEN eventName='Shot'
                     AND subEventName LIKE '%Goal%' THEN 1 END) AS goals,
            SUM(CASE WHEN eventName='Pass' THEN 1 END)          AS total_passes
        FROM football_events
        WHERE playerName = '{player_name}'
        GROUP BY playerName, teamName
    \"\"\").toPandas()
    return df.iloc[0].to_dict()
        """, language="python")
