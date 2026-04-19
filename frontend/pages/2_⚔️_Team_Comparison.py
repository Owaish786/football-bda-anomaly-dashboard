"""
pages/2_⚔️_Team_Comparison.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from api_connector import get_team_stats, get_team_form, get_event_distribution, ALL_TEAMS, TEAMS_ENGLAND, TEAMS_SPAIN

st.set_page_config(page_title="Team Comparison · Football BDA", page_icon="⚔️", layout="wide")

SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600;700&display=swap');
:root{--green:#00FF87;--dark:#0a0e1a;--card:#111827;--card2:#1a2235;--border:#1f2d45;--text:#e2e8f0;--muted:#64748b;--blue:#3b82f6;--orange:#f97316;}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--text);}
.stApp{background:linear-gradient(135deg,#060b18 0%,#0d1424 50%,#060b18 100%);}
[data-testid="stSidebar"]{background:var(--card)!important;border-right:1px solid var(--border);}
h1,h2,h3{font-family:'Bebas Neue',sans-serif;letter-spacing:1px;}
.block-container{padding-top:1.5rem;}
.section-header{border-left:4px solid var(--green);padding-left:.7rem;margin:1.5rem 0 1rem;font-family:'Bebas Neue',sans-serif;font-size:1.4rem;letter-spacing:1px;}
.team-header{border-radius:12px;padding:1.2rem;text-align:center;}
.team-a{background:linear-gradient(135deg,#0c2340,#1a3a6e);border:2px solid #3b82f6;}
.team-b{background:linear-gradient(135deg,#1a1a00,#3d3000);border:2px solid #f97316;}
.vs-badge{background:#111827;border:2px solid #00FF87;border-radius:50%;width:50px;height:50px;display:flex;align-items:center;justify-content:center;font-family:'Bebas Neue',sans-serif;font-size:1.1rem;color:#00FF87;margin:auto;}
.metric-row{display:flex;align-items:center;margin:.35rem 0;gap:8px;}
.metric-bar-bg{flex:1;height:10px;background:#1f2d45;border-radius:5px;overflow:hidden;}
.metric-bar-fill{height:100%;border-radius:5px;}
.bar-blue{background:linear-gradient(90deg,#1d4ed8,#3b82f6);}
.bar-orange{background:linear-gradient(90deg,#c2410c,#f97316);}
.form-badge{display:inline-block;width:26px;height:26px;border-radius:50%;text-align:center;line-height:26px;font-weight:700;font-size:.8rem;margin:2px;}
.form-W{background:#16a34a;color:#fff;} .form-D{background:#ca8a04;color:#fff;} .form-L{background:#dc2626;color:#fff;}
.stButton>button{background:#00FF87;color:#000;font-weight:700;border:none;border-radius:8px;padding:.5rem 1.5rem;}
</style>
"""
st.markdown(SHARED_CSS, unsafe_allow_html=True)

PLOTLY_DARK = "#0d1424"
BLUE = "#3b82f6"
ORANGE = "#f97316"

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style="font-size:2.8rem;color:#00FF87;margin-bottom:0;">⚔️ TEAM COMPARISON</h1>
<p style="color:#64748b;margin-top:.3rem;">Select two teams to compare head-to-head stats</p>
""", unsafe_allow_html=True)

# ── Team Selection ────────────────────────────────────────────────────────────
sc1, sc2, sc3 = st.columns([5, 1, 5])

with sc1:
    league_a = st.selectbox("League (Team A)", ["All", "England", "Spain"], key="la")
    pool_a = TEAMS_ENGLAND if league_a == "England" else (TEAMS_SPAIN if league_a == "Spain" else ALL_TEAMS)
    team_a = st.selectbox("🔵 Team A", pool_a, index=0, key="ta")

with sc2:
    st.markdown("<br><br><div class='vs-badge'>VS</div>", unsafe_allow_html=True)

with sc3:
    league_b = st.selectbox("League (Team B)", ["All", "England", "Spain"], index=2, key="lb")
    pool_b = TEAMS_ENGLAND if league_b == "England" else (TEAMS_SPAIN if league_b == "Spain" else ALL_TEAMS)
    default_b = min(1, len(pool_b) - 1)
    team_b = st.selectbox("🟠 Team B", pool_b, index=default_b, key="tb")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("⚡ Compare Teams", width="content"):
    st.session_state["compare_clicked"] = True

if not st.session_state.get("compare_clicked") and team_a and team_b:
    st.session_state["compare_clicked"] = True

if st.session_state.get("compare_clicked") and team_a and team_b:
    sa = get_team_stats(team_a)
    sb = get_team_stats(team_b)

    # ── Team Headers ──────────────────────────────────────────────────────────
    h1, h2, h3 = st.columns([5, 1, 5])
    with h1:
        st.markdown(f"""
        <div class="team-header team-a">
            <div style="font-size:2.2rem;">🔵</div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:1.6rem;color:#93c5fd;letter-spacing:1px;">{team_a}</div>
            <div style="color:#64748b;font-size:.82rem;">Pts: <b style="color:#3b82f6">{sa['points']}</b> &nbsp;|&nbsp; Rank: <b style="color:#3b82f6">TBD</b></div>
        </div>""", unsafe_allow_html=True)
    with h2:
        st.markdown("<div style='text-align:center;padding-top:2rem;font-family:\"Bebas Neue\",sans-serif;font-size:1.4rem;color:#64748b;'>VS</div>", unsafe_allow_html=True)
    with h3:
        st.markdown(f"""
        <div class="team-header team-b">
            <div style="font-size:2.2rem;">🟠</div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:1.6rem;color:#fdba74;letter-spacing:1px;">{team_b}</div>
            <div style="color:#64748b;font-size:.82rem;">Pts: <b style="color:#f97316">{sb['points']}</b> &nbsp;|&nbsp; Rank: <b style="color:#f97316">TBD</b></div>
        </div>""", unsafe_allow_html=True)

    # ── KPI Row ───────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">KEY STATS AT A GLANCE</div>', unsafe_allow_html=True)

    kpi_fields = [
        ("Matches", "matches_played"),
        ("Wins",    "wins"),
        ("Draws",   "draws"),
        ("Losses",  "losses"),
        ("Goals",   "goals_scored"),
        ("Points",  "points"),
    ]
    cols = st.columns(len(kpi_fields))
    for col, (label, key) in zip(cols, kpi_fields):
        va, vb = sa[key], sb[key]
        color_a = "#3b82f6"
        color_b = "#f97316"
        if va > vb:   color_a = "#00FF87"
        elif vb > va: color_b = "#00FF87"
        col.markdown(f"""
        <div style="background:#111827;border:1px solid #1f2d45;border-radius:10px;padding:.8rem;text-align:center;">
            <div style="font-size:.7rem;color:#64748b;text-transform:uppercase;letter-spacing:.8px;margin-bottom:.3rem;">{label}</div>
            <div style="display:flex;justify-content:center;align-items:center;gap:.6rem;">
                <span style="font-family:'Bebas Neue',sans-serif;font-size:1.6rem;color:{color_a};">{va}</span>
                <span style="color:#1f2d45;">|</span>
                <span style="font-family:'Bebas Neue',sans-serif;font-size:1.6rem;color:{color_b};">{vb}</span>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Horizontal bar comparison ─────────────────────────────────────────────
    st.markdown('<div class="section-header">DETAILED COMPARISON</div>', unsafe_allow_html=True)

    metrics = [
        ("Win %",          "win_pct",        100),
        ("Pass Accuracy",  "pass_accuracy",  100),
        ("Goals Scored",   "goals_scored",   100),
        ("Shots",          "shots",          500),
        ("Shots on Target","shots_on_target",300),
        ("Possession %",   "possession_pct", 100),
        ("Total Passes",   "total_passes",   25000),
        ("Fouls",          "fouls",          700),
    ]

    rows_html = []
    for label, key, max_val in metrics:
        va = sa[key]; vb = sb[key]
        pct_a = min(va / max_val * 100, 100)
        pct_b = min(vb / max_val * 100, 100)
        winner_a = "font-weight:700;color:#00FF87;" if va > vb else ""
        winner_b = "font-weight:700;color:#00FF87;" if vb > va else ""
        unit = "%" if key in ("win_pct","pass_accuracy","possession_pct") else ""
        rows_html.append(f"""
        <div style="background:#111827;border:1px solid #1f2d45;border-radius:8px;padding:.8rem 1.2rem;margin:.4rem 0;">
            <div style="display:grid;grid-template-columns:1fr 160px 1fr;gap:.8rem;align-items:center;">
                <div style="text-align:right;">
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;color:#3b82f6;{winner_a}">{va}{unit}</div>
                    <div style="height:8px;background:#1f2d45;border-radius:4px;overflow:hidden;margin-top:3px;">
                        <div style="height:100%;width:{pct_a}%;background:linear-gradient(90deg,#1d4ed8,#3b82f6);border-radius:4px;float:right;"></div>
                    </div>
                </div>
                <div style="text-align:center;font-size:.8rem;color:#64748b;text-transform:uppercase;letter-spacing:.8px;">{label}</div>
                <div style="text-align:left;">
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;color:#f97316;{winner_b}">{vb}{unit}</div>
                    <div style="height:8px;background:#1f2d45;border-radius:4px;overflow:hidden;margin-top:3px;">
                        <div style="height:100%;width:{pct_b}%;background:linear-gradient(90deg,#c2410c,#f97316);border-radius:4px;"></div>
                    </div>
                </div>
            </div>
        </div>""")
    st.markdown("".join(rows_html), unsafe_allow_html=True)

    # ── Radar Chart ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">PERFORMANCE RADAR</div>', unsafe_allow_html=True)

    radar_cats = ["Win %","Pass Acc","Goals","Shots OT %","Possession","Pts/Match"]
    def normalize(sa, sb, key, divisor=1):
        va = sa[key] / divisor
        vb = sb[key] / divisor
        mx = max(va, vb, 1)
        return round(va / mx * 100, 1), round(vb / mx * 100, 1)

    pairs = [
        normalize(sa, sb, "win_pct"),
        normalize(sa, sb, "pass_accuracy"),
        normalize(sa, sb, "goals_scored"),
        (round(sa["shots_on_target"]/max(sa["shots"],1)*100,1),
         round(sb["shots_on_target"]/max(sb["shots"],1)*100,1)),
        normalize(sa, sb, "possession_pct"),
        normalize(sa, sb, "points", sa["matches_played"]),
    ]
    vals_a = [p[0] for p in pairs]
    vals_b = [p[1] for p in pairs]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=vals_a + [vals_a[0]], theta=radar_cats + [radar_cats[0]],
        fill="toself", name=team_a,
        line=dict(color=BLUE, width=2),
        fillcolor="rgba(59,130,246,0.15)"
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=vals_b + [vals_b[0]], theta=radar_cats + [radar_cats[0]],
        fill="toself", name=team_b,
        line=dict(color=ORANGE, width=2),
        fillcolor="rgba(249,115,22,0.15)"
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0,110], gridcolor="#1f2d45", tickfont=dict(color="#64748b",size=9)),
            angularaxis=dict(gridcolor="#1f2d45", tickfont=dict(color="#e2e8f0",size=10))
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0"),
        height=420,
        margin=dict(t=30, b=30),
    )
    st.plotly_chart(fig_radar, width="stretch")

    # ── Event Distribution Grouped Bar ────────────────────────────────────────
    st.markdown('<div class="section-header">EVENT DISTRIBUTION</div>', unsafe_allow_html=True)

    ev_a = get_event_distribution(team_a)
    ev_b = get_event_distribution(team_b)
    ev_cats = list(ev_a.keys())

    fig_ev = go.Figure(data=[
        go.Bar(name=team_a, x=ev_cats, y=list(ev_a.values()), marker_color=BLUE),
        go.Bar(name=team_b, x=ev_cats, y=list(ev_b.values()), marker_color=ORANGE),
    ])
    fig_ev.update_layout(
        barmode="group",
        plot_bgcolor=PLOTLY_DARK, paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0", font_family="DM Sans",
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="#1f2d45", tickangle=-20),
        yaxis=dict(gridcolor="#1f2d45"),
        margin=dict(t=20, b=10),
        height=350,
    )
    st.plotly_chart(fig_ev, width="stretch")

    # ── Form ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">RECENT FORM (LAST 5)</div>', unsafe_allow_html=True)
    f1, f2 = st.columns(2)
    def form_badges(team):
        form = get_team_form(team)
        badges = "".join(f'<span class="form-badge form-{r}">{r}</span>' for r in form)
        return f"""
        <div style="background:#111827;border:1px solid #1f2d45;border-radius:8px;padding:.8rem 1rem;">
            <div style="font-size:.78rem;color:#64748b;margin-bottom:.4rem;text-transform:uppercase;">{team}</div>
            {badges}
        </div>"""
    f1.markdown(form_badges(team_a), unsafe_allow_html=True)
    f2.markdown(form_badges(team_b), unsafe_allow_html=True)

    # ── Goal Difference Chart ─────────────────────────────────────────────────
    st.markdown('<div class="section-header">ATTACK vs DEFENCE</div>', unsafe_allow_html=True)
    fig_atk = go.Figure()
    for team, stats, color in [(team_a, sa, BLUE), (team_b, sb, ORANGE)]:
        fig_atk.add_trace(go.Bar(
            x=[team], y=[stats["goals_scored"]], name="Goals Scored",
            marker_color=color, text=[stats["goals_scored"]], textposition="outside"
        ))
        fig_atk.add_trace(go.Bar(
            x=[team], y=[-stats["goals_against"]], name="Goals Against",
            marker_color="#ef4444", text=[stats["goals_against"]], textposition="outside",
            showlegend=team == team_a
        ))
    fig_atk.update_layout(
        barmode="relative",
        plot_bgcolor=PLOTLY_DARK, paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        xaxis=dict(gridcolor="#1f2d45"),
        yaxis=dict(gridcolor="#1f2d45", title="Goals"),
        height=340, margin=dict(t=20, b=10),
    )
    st.plotly_chart(fig_atk, width="stretch")

    with st.expander("🔌 Backend Integration Note"):
        st.code("""
# Replace get_team_stats() in data/mock_data.py:

def get_team_stats(team_name: str) -> dict:
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.getOrCreate()
    result = spark.sql(f\"\"\"
        SELECT
            COUNT(DISTINCT matchId)                     AS matches_played,
            SUM(CASE WHEN eventName = 'Shot'
                     AND tags LIKE '%Goal%' THEN 1 END) AS goals_scored,
            SUM(CASE WHEN eventName = 'Pass' THEN 1 END) AS total_passes
        FROM football_events
        WHERE teamName = '{team_name}'
    \"\"\").toPandas().iloc[0]
    return result.to_dict()
        """, language="python")
