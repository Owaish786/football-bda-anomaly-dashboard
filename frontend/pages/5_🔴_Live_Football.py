"""
pages/5_🔴_Live_Football.py
Live football data dashboard (scores, fixtures, standings, team/player stats, events, predictions).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import streamlit as st

from api_connector import (
    get_live_fixtures,
    get_live_player_stats,
    get_live_scores,
    get_live_standings,
    get_live_team_stats,
    get_match_events,
    get_match_prediction,
)

st.set_page_config(page_title="Live Football API", page_icon="🔴", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;700&family=Manrope:wght@400;600;700&display=swap');
:root{
  --bg1:#090f1f;
  --bg2:#101a34;
  --card:#121d3a;
  --line:#24345f;
  --text:#e6efff;
  --muted:#8ea1c9;
  --red:#ff3d57;
  --cyan:#25d5ff;
  --lime:#8dfc8d;
}
html,body,[class*="css"]{font-family:'Manrope',sans-serif;color:var(--text);}
.stApp{
  background:
    radial-gradient(circle at 5% 5%, rgba(255,61,87,.20), transparent 32%),
    radial-gradient(circle at 90% 15%, rgba(37,213,255,.20), transparent 35%),
    linear-gradient(125deg,var(--bg1) 0%,var(--bg2) 55%,#0a1225 100%);
}
[data-testid="stSidebar"]{background:#0b1430!important;border-right:1px solid var(--line);}
h1,h2,h3{font-family:'Chakra Petch',sans-serif;letter-spacing:.6px;}
.block-container{padding-top:1.2rem;}
.hero{
  border:1px solid var(--line);
  border-radius:16px;
  padding:1rem 1.2rem;
  background:linear-gradient(150deg, rgba(255,61,87,.16), rgba(37,213,255,.10));
}
.section-title{
  margin:1rem 0 .55rem;
  border-left:4px solid var(--cyan);
  padding-left:.55rem;
  font-family:'Chakra Petch',sans-serif;
}
.stat-card{
  border:1px solid var(--line);
  border-radius:12px;
  padding:.75rem .9rem;
  background:linear-gradient(150deg, #111a34, #162548);
}
.label{font-size:.74rem;color:var(--muted);text-transform:uppercase;letter-spacing:.8px;}
.value{font-family:'Chakra Petch',sans-serif;font-size:1.45rem;line-height:1.15;}
</style>
""",
    unsafe_allow_html=True,
)

SUPPORTED_LEAGUES = {
    39: "England - Premier League",
    140: "Spain - La Liga",
}

st.markdown(
    """
<div class="hero">
  <h1 style="margin:0;font-size:2.1rem;">🔴 Live Football Control Center</h1>
  <p style="margin:.45rem 0 0;color:#9ab0d7;">Live scores, fixtures, standings, team stats, player stats, match events, and predictions from your backend.</p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("<div class='section-title'>Auto Live Mode</div>", unsafe_allow_html=True)
st.caption("Showing only England and Spain leagues (model training scope).")

scores = get_live_scores()
fixtures = get_live_fixtures()

scores_data = [
    item for item in scores.get("data", [])
    if int((item.get("league", {}) or {}).get("id", -1)) in SUPPORTED_LEAGUES
] if isinstance(scores.get("data", []), list) else []

fixtures_data = [
    item for item in fixtures.get("data", [])
    if int((item.get("league", {}) or {}).get("id", -1)) in SUPPORTED_LEAGUES
] if isinstance(fixtures.get("data", []), list) else []

featured_league = None
featured_season = None
if fixtures_data:
    first_fixture = fixtures_data[0]
    league_info = first_fixture.get("league", {})
    featured_league = league_info.get("id")
    featured_season = league_info.get("season")

if featured_league and featured_season:
    standings = get_live_standings(league=int(featured_league), season=int(featured_season))
else:
    standings = {
        "success": False,
        "error": "No active fixture context available for standings.",
        "data": [],
    }

live_matches_count = len(scores_data)
fixtures_count = len(fixtures_data)
standings_count = len(standings.get("data", [])) if isinstance(standings.get("data", []), list) else 0

k1, k2, k3 = st.columns(3)
k1.markdown(f"<div class='stat-card'><div class='label'>Live Matches</div><div class='value'>{live_matches_count}</div></div>", unsafe_allow_html=True)
k2.markdown(f"<div class='stat-card'><div class='label'>Fixtures Loaded</div><div class='value'>{fixtures_count}</div></div>", unsafe_allow_html=True)
k3.markdown(f"<div class='stat-card'><div class='label'>Standings Groups</div><div class='value'>{standings_count}</div></div>", unsafe_allow_html=True)

st.markdown("<div class='section-title'>Live Scores</div>", unsafe_allow_html=True)
if not scores.get("success"):
    st.warning(scores.get("error", "Unable to fetch live scores."))
else:
    rows = []
    for item in scores_data:
        fixture = item.get("fixture", {})
        teams = item.get("teams", {})
        goals = item.get("goals", {})
        status = fixture.get("status", {})
        league_info = item.get("league", {})
        rows.append(
            {
                "fixture_id": fixture.get("id"),
                "league": league_info.get("name"),
                "home": teams.get("home", {}).get("name"),
                "away": teams.get("away", {}).get("name"),
                "score": f"{goals.get('home', 0)} - {goals.get('away', 0)}",
                "minute": status.get("elapsed"),
                "status": status.get("short"),
            }
        )
    if rows:
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    else:
        st.info("No matches are live right now.")

st.markdown("<div class='section-title'>Upcoming Fixtures</div>", unsafe_allow_html=True)
if not fixtures.get("success"):
    st.warning(fixtures.get("error", "Unable to fetch fixtures."))
else:
    rows = []
    for item in fixtures_data:
        fixture = item.get("fixture", {})
        teams = item.get("teams", {})
        status = fixture.get("status", {})
        league_info = item.get("league", {})
        status_short = status.get("short")
        # Upcoming = not started entries from today's feed (works on free plans).
        if status_short not in {"NS", "TBD"}:
            continue
        rows.append(
            {
                "fixture_id": fixture.get("id"),
                "date": fixture.get("date"),
                "league": league_info.get("name"),
                "home": teams.get("home", {}).get("name"),
                "away": teams.get("away", {}).get("name"),
                "status": status_short,
            }
        )
    if rows:
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    else:
        st.info("No upcoming fixtures found for the current feed window.")

st.markdown("<div class='section-title'>Standings</div>", unsafe_allow_html=True)
if not standings.get("success"):
    st.warning(standings.get("error", "Unable to fetch standings."))
else:
    table_rows = []
    for block in standings.get("data", []):
        league_block = block.get("league", {})
        for group in league_block.get("standings", []):
            for team_row in group:
                team = team_row.get("team", {})
                all_stats = team_row.get("all", {})
                table_rows.append(
                    {
                        "rank": team_row.get("rank"),
                        "team": team.get("name"),
                        "points": team_row.get("points"),
                        "played": all_stats.get("played"),
                        "win": all_stats.get("win"),
                        "draw": all_stats.get("draw"),
                        "lose": all_stats.get("lose"),
                        "goals_for": (all_stats.get("goals") or {}).get("for"),
                        "goals_against": (all_stats.get("goals") or {}).get("against"),
                    }
                )
    standings_df = pd.DataFrame(table_rows).sort_values("rank") if table_rows else pd.DataFrame()
    if not standings_df.empty:
        st.dataframe(standings_df, width="stretch", hide_index=True)
    else:
        st.info("No standings rows found for the selected live context.")

st.markdown("<div class='section-title'>Team Stats and Player Stats</div>", unsafe_allow_html=True)
f1, f2, f3 = st.columns([2, 2, 2])
with f1:
    league_label = st.selectbox("League (details)", options=list(SUPPORTED_LEAGUES.values()), index=0)
    league = next(k for k, v in SUPPORTED_LEAGUES.items() if v == league_label)
with f2:
    season = st.number_input("Season (details)", min_value=2000, value=2026, step=1)
with f3:
    team_id = st.number_input("Team ID (details)", min_value=1, value=33, step=1)

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Team Stats")
    team_stats = get_live_team_stats(team=int(team_id), league=int(league), season=int(season))
    if not team_stats.get("success"):
        st.warning(team_stats.get("error", "Unable to fetch team stats."))
    else:
        team_payload = team_stats.get("data", {})
        if isinstance(team_payload, list):
            st.json(team_payload[0] if team_payload else {})
        elif isinstance(team_payload, dict):
            st.json(team_payload)
        else:
            st.json({})

with col_b:
    st.subheader("Player Stats")
    player_stats = get_live_player_stats(team=int(team_id), season=int(season), league=int(league), page=1)
    if not player_stats.get("success"):
        st.warning(player_stats.get("error", "Unable to fetch player stats."))
    else:
        players = player_stats.get("data", [])
        compact = []
        for item in players[:20]:
            player = item.get("player", {})
            stats = (item.get("statistics") or [{}])[0]
            goals = stats.get("goals", {})
            shots = stats.get("shots", {})
            compact.append(
                {
                    "player_id": player.get("id"),
                    "player": player.get("name"),
                    "team": (stats.get("team") or {}).get("name"),
                    "goals": goals.get("total"),
                    "assists": goals.get("assists"),
                    "shots": shots.get("total"),
                    "shots_on": shots.get("on"),
                }
            )
        st.dataframe(pd.DataFrame(compact), width="stretch", hide_index=True)

st.markdown("<div class='section-title'>Match Events and Prediction</div>", unsafe_allow_html=True)
fixture_id = st.number_input("Fixture ID", min_value=1, value=215662, step=1)

c1, c2 = st.columns(2)
with c1:
    if st.button("Load Match Events", width="stretch"):
        events = get_match_events(fixture=int(fixture_id))
        if not events.get("success"):
            st.warning(events.get("error", "Unable to fetch match events."))
        else:
            rows = []
            for e in events.get("data", []):
                team = e.get("team", {})
                player = e.get("player", {})
                time_data = e.get("time", {})
                rows.append(
                    {
                        "minute": time_data.get("elapsed"),
                        "extra": time_data.get("extra"),
                        "team": team.get("name"),
                        "player": player.get("name"),
                        "type": e.get("type"),
                        "detail": e.get("detail"),
                    }
                )
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

with c2:
    if st.button("Load Prediction", width="stretch"):
        prediction = get_match_prediction(fixture=int(fixture_id))
        if not prediction.get("success"):
            st.warning(prediction.get("error", "Unable to fetch prediction."))
        else:
            payload = prediction.get("data", prediction)
            if isinstance(payload, list):
                st.json(payload[0] if payload else {})
            elif isinstance(payload, dict):
                st.json(payload)
            else:
                st.json({})
