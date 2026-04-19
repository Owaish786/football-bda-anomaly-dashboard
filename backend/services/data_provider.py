"""
Data provider for API routes.
Loads real processed data and exposes helper accessors for endpoints.
"""

import json
from pathlib import Path


def load_processed_results():
    """Load processed data from JSON file if present."""
    results_file = Path(__file__).parent.parent.parent / "data" / "processed_results.json"
    if not results_file.exists():
        return None

    try:
        with open(results_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


REAL_DATA = load_processed_results()


def get_teams_for_rankings():
    """Return real team rankings if available, otherwise fallback list."""
    if REAL_DATA and REAL_DATA.get("team_stats"):
        teams = []
        for idx, team in enumerate(REAL_DATA["team_stats"], start=1):
            passes = team.get("passes", 0)
            shots = team.get("shots", 0)
            fouls = max(team.get("fouls", 1), 1)
            matches = max(team.get("matches", 1), 1)
            total_events = max(team.get("total_events", 1), 1)

            ranking_score = (shots * 10 + passes * 0.1 + (passes / fouls) * 10) / matches
            teams.append(
                {
                    "rank": idx,
                    "teamName": team.get("teamName", f"Team {idx}"),
                    "ranking_score": round(ranking_score, 2),
                    "total_matches": team.get("matches", 0),
                    "shots": shots,
                    "passes": passes,
                    "pass_accuracy": round((passes / total_events) * 100, 2),
                }
            )

        return sorted(teams, key=lambda x: x["ranking_score"], reverse=True)

    return [
        {"rank": 1, "teamName": "Manchester City", "ranking_score": 95.5, "total_matches": 38, "shots": 1250, "passes": 28500, "pass_accuracy": 87.5},
        {"rank": 2, "teamName": "Arsenal", "ranking_score": 93.2, "total_matches": 38, "shots": 1180, "passes": 27800, "pass_accuracy": 86.2},
        {"rank": 3, "teamName": "Liverpool", "ranking_score": 91.8, "total_matches": 38, "shots": 1100, "passes": 26500, "pass_accuracy": 85.5},
    ]


def get_team_comparison(team1, team2):
    """Return simple comparison payload."""
    return {
        "team1": {
            "teamName": team1,
            "total_events": 15234,
            "total_matches": 38,
            "passes": 8500,
            "shots": 520,
            "fouls": 350,
            "tackles": 890,
            "passes_success_rate": 85.5,
        },
        "team2": {
            "teamName": team2,
            "total_events": 14892,
            "total_matches": 38,
            "passes": 8200,
            "shots": 480,
            "fouls": 380,
            "tackles": 920,
            "passes_success_rate": 82.3,
        },
        "comparison": {
            "events_diff": 342,
            "passes_diff": 300,
            "shots_diff": 40,
            "pass_accuracy_diff": 3.2,
        },
    }


def get_player_comparison(player1, player2):
    """Return simple comparison payload for two players."""
    return {
        "player1": {
            "playerName": player1,
            "team": "Team 1",
            "total_events": 1250,
            "passes": 750,
            "shots": 85,
            "fouls": 12,
            "tackles": 45,
            "interceptions": 28,
            "avg_event_minute": 45.5,
        },
        "player2": {
            "playerName": player2,
            "team": "Team 2",
            "total_events": 1180,
            "passes": 680,
            "shots": 92,
            "fouls": 15,
            "tackles": 52,
            "interceptions": 32,
            "avg_event_minute": 46.2,
        },
        "comparison": {
            "events_diff": 70,
            "passes_diff": 70,
            "shots_diff": -7,
            "tackles_diff": -7,
        },
    }


def get_teams_list():
    """Return real teams when available, fallback otherwise."""
    if REAL_DATA and REAL_DATA.get("teams"):
        return REAL_DATA["teams"]

    return [
        "Manchester City",
        "Arsenal",
        "Liverpool",
        "Chelsea",
        "Manchester United",
        "Tottenham",
        "Real Madrid",
        "Barcelona",
    ]


def get_players_list(team=None):
    """Return real players when available, fallback otherwise."""
    if REAL_DATA and REAL_DATA.get("players"):
        players = [p for p in REAL_DATA["players"] if isinstance(p, str) and p.strip()]
        return players[:200]

    return [
        "Erling Haaland",
        "Harry Kane",
        "Kylian Mbappe",
        "Lionel Messi",
        "Kevin De Bruyne",
    ]
