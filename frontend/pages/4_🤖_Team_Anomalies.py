"""
pages/4_🤖_Team_Anomalies.py
Tailwind-inspired anomaly monitoring UI for IsolationForest output.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import plotly.express as px
import streamlit as st

from api_connector import get_team_anomalies

st.set_page_config(page_title="Team Anomalies · Football BDA", page_icon="🤖", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Manrope:wght@400;500;600;700&display=swap');
:root{
  --bg-1:#030711;
  --bg-2:#0b1223;
  --card:#0f172a;
  --card-2:#111c33;
  --line:#1e293b;
  --text:#dbe7ff;
  --muted:#7f95b8;
  --ok:#22c55e;
  --warn:#f59e0b;
  --bad:#ef4444;
  --cyan:#22d3ee;
  --indigo:#6366f1;
}
html,body,[class*="css"]{font-family:'Manrope',sans-serif;color:var(--text);}
.stApp{background:
  radial-gradient(circle at 12% 18%, rgba(34,211,238,.14), transparent 28%),
  radial-gradient(circle at 82% 10%, rgba(99,102,241,.15), transparent 32%),
  linear-gradient(120deg, var(--bg-1) 0%, var(--bg-2) 52%, #040915 100%);
}
[data-testid="stSidebar"]{background:#0a1326!important;border-right:1px solid var(--line);}
.block-container{padding-top:1.25rem;}
h1,h2,h3{font-family:'Sora',sans-serif;letter-spacing:.2px;}
.hero{
  border:1px solid #25324b;
  border-radius:18px;
  padding:1.3rem 1.2rem;
  background:linear-gradient(145deg, rgba(99,102,241,.16), rgba(34,211,238,.09));
  box-shadow:0 12px 40px rgba(2,8,23,.35);
}
.stat-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:10px;}
.stat-card{
  background:linear-gradient(160deg, #0f172a 0%, #111c33 100%);
  border:1px solid #263551;
  border-radius:14px;
  padding:.9rem 1rem;
}
.stat-label{font-size:.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:.8px;}
.stat-value{font-family:'Sora',sans-serif;font-weight:700;font-size:1.45rem;line-height:1.1;margin-top:.25rem;}
.badge{
  display:inline-block;
  border-radius:999px;
  padding:.28rem .72rem;
  font-size:.74rem;
  font-weight:700;
  letter-spacing:.3px;
}
.badge-ok{background:rgba(34,197,94,.18);border:1px solid rgba(34,197,94,.45);color:#86efac;}
.badge-bad{background:rgba(239,68,68,.18);border:1px solid rgba(239,68,68,.45);color:#fca5a5;}
.section-title{
  margin:1.4rem 0 .75rem;
  font-family:'Sora',sans-serif;
  font-size:1.1rem;
  color:#cfe5ff;
  border-left:4px solid #22d3ee;
  padding-left:.55rem;
}
[data-testid="metric-container"]{
  background:linear-gradient(165deg,#0f172a,#111c33);
  border:1px solid #263551;
  border-radius:12px;
  padding:.8rem .95rem;
}
[data-testid="stMetricLabel"]{color:var(--muted)!important;}
[data-testid="stMetricValue"]{color:#c7dcff!important;font-family:'Sora',sans-serif;}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero">
  <h1 style="margin:0;color:#d8e7ff;font-size:2rem;">🤖 Team Anomaly Monitor</h1>
  <p style="margin:.55rem 0 0;color:#96add3;max-width:860px;">
    IsolationForest scans team event profiles and flags unusual behavior patterns based on shots, passes, fouls,
    total events, and matches.
  </p>
</div>
""",
    unsafe_allow_html=True,
)

f1, f2, f3 = st.columns([2, 1, 1])
with f1:
    contamination = st.slider("Contamination", min_value=0.01, max_value=0.50, value=0.20, step=0.01)
with f2:
    top_n = st.selectbox("Top anomalies", [3, 5, 8, 10, 15], index=3)
with f3:
    refresh = st.button("Refresh", width="stretch")

if refresh:
    st.rerun()

result = get_team_anomalies(contamination=contamination, top_n=top_n)

data = result.get("data", [])
df = pd.DataFrame(data)

model_name = result.get("model", "IsolationForest")
detected = int(result.get("detected_anomalies", 0) or 0)
total_teams = int(result.get("total_teams", 0) or 0)

st.markdown('<div class="section-title">Snapshot</div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Model", model_name)
m2.metric("Total Teams Scanned", total_teams)
m3.metric("Detected Anomalies", detected)
rate = (detected / total_teams * 100.0) if total_teams else 0.0
m4.metric("Anomaly Rate", f"{rate:.1f}%")

if not result.get("success"):
    st.error(result.get("error", "Could not load anomaly data."))

if df.empty:
    st.warning("No anomaly rows returned for the current settings.")
else:
    if "anomaly_score" in df.columns:
        df = df.sort_values("anomaly_score", ascending=True).reset_index(drop=True)

    st.markdown('<div class="section-title">Flagged Teams</div>', unsafe_allow_html=True)

    show_df = df.copy()
    if "anomaly_score" in show_df.columns:
        show_df["anomaly_score"] = show_df["anomaly_score"].map(lambda x: round(float(x), 5))

    preferred_cols = [
        "teamName",
        "anomaly_label",
        "anomaly_score",
        "shots",
        "passes",
        "fouls",
        "total_events",
        "matches",
    ]
    cols = [c for c in preferred_cols if c in show_df.columns]
    st.dataframe(show_df[cols], width="stretch", hide_index=True)

    c1, c2 = st.columns(2)

    with c1:
        if "anomaly_score" in df.columns and "teamName" in df.columns:
            fig_score = px.bar(
                df,
                x="teamName",
                y="anomaly_score",
                color="anomaly_score",
                color_continuous_scale=[[0, "#ef4444"], [1, "#22d3ee"]],
                title="Anomaly Score by Team (lower = more anomalous)",
            )
            fig_score.update_layout(
                plot_bgcolor="#0b1223",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#dbe7ff",
                xaxis=dict(tickangle=-25, gridcolor="#22304a"),
                yaxis=dict(gridcolor="#22304a"),
                coloraxis_showscale=False,
                margin=dict(t=56, b=20),
            )
            st.plotly_chart(fig_score, width="stretch")

    with c2:
        if all(col in df.columns for col in ["passes", "shots", "teamName"]):
            fig_profile = px.scatter(
                df,
                x="passes",
                y="shots",
                size="total_events" if "total_events" in df.columns else None,
                color="anomaly_label" if "anomaly_label" in df.columns else None,
                hover_name="teamName",
                title="Team Event Profile (passes vs shots)",
                color_discrete_map={"anomaly": "#ef4444", "normal": "#22c55e"},
            )
            fig_profile.update_layout(
                plot_bgcolor="#0b1223",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#dbe7ff",
                xaxis=dict(gridcolor="#22304a"),
                yaxis=dict(gridcolor="#22304a"),
                margin=dict(t=56, b=20),
            )
            st.plotly_chart(fig_profile, width="stretch")

st.markdown(
    """
<div style="margin-top:1rem;padding:.9rem 1rem;border:1px solid #27344f;border-radius:12px;background:rgba(15,23,42,.6);">
  <span class="badge badge-ok">Normal</span>
  <span style="color:#8ca4c8;font-size:.86rem;margin-left:.45rem;">Team follows expected event distribution.</span>
  <br/>
  <span class="badge badge-bad" style="margin-top:.45rem;">Anomaly</span>
  <span style="color:#8ca4c8;font-size:.86rem;margin-left:.45rem;">Team behavior is statistically unusual and worth deeper analysis.</span>
</div>
""",
    unsafe_allow_html=True,
)
