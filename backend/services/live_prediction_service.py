"""
Hybrid match prediction service.
Uses PySpark-processed historical team stats as the primary signal,
then blends in live league context from API feed.
"""

import math
import unicodedata
from typing import Any, Dict, Optional

from backend.services.data_provider import REAL_DATA


class LiveMatchPredictionService:
    """Predict fixture outcome using processed data + live context."""

    SUPPORTED_LEAGUES = {
        39: "Premier League",
        140: "La Liga",
    }

    def __init__(self, live_service) -> None:
        self.live_service = live_service
        self.team_stats = (REAL_DATA or {}).get("team_stats", []) if REAL_DATA else []
        self.team_index = self._build_team_index(self.team_stats)
        self.bounds = self._compute_bounds(self.team_stats)

    def predict_fixture(self, fixture_id: int) -> Dict[str, Any]:
        fixture_payload = self.live_service.get_fixture_by_id(fixture=fixture_id)
        if not fixture_payload.get("success"):
            return {
                "success": False,
                "error": "Could not fetch fixture data for prediction",
                "fixture_id": fixture_id,
                "upstream": fixture_payload,
            }

        fixtures = fixture_payload.get("data", [])
        if not fixtures:
            return {
                "success": False,
                "error": "Fixture not found",
                "fixture_id": fixture_id,
            }

        item = fixtures[0]
        fixture = item.get("fixture", {})
        league = item.get("league", {})
        teams = item.get("teams", {})

        home_team = teams.get("home", {})
        away_team = teams.get("away", {})
        home_name = home_team.get("name", "Home")
        away_name = away_team.get("name", "Away")
        home_id = home_team.get("id")
        away_id = away_team.get("id")

        league_id = league.get("id")
        season = league.get("season")

        if int(league_id or -1) not in self.SUPPORTED_LEAGUES:
            supported = ", ".join(f"{lid} ({name})" for lid, name in self.SUPPORTED_LEAGUES.items())
            return {
                "success": False,
                "error": "Prediction is available only for supported training leagues",
                "fixture_id": fixture_id,
                "league_id": league_id,
                "league_name": league.get("name"),
                "supported_leagues": supported,
            }

        home_processed = self._processed_strength(home_name)
        away_processed = self._processed_strength(away_name)

        home_live = self._live_strength(team_id=home_id, league_id=league_id, season=season)
        away_live = self._live_strength(team_id=away_id, league_id=league_id, season=season)

        # Processed data is the main signal; live data updates current form.
        home_strength = 0.7 * home_processed["score"] + 0.3 * home_live["score"]
        away_strength = 0.7 * away_processed["score"] + 0.3 * away_live["score"]

        home_advantage = 0.04
        delta = (home_strength + home_advantage) - away_strength

        home_prob_raw = self._sigmoid(3.1 * delta)
        draw_prob_raw = max(0.12, min(0.32, 0.28 - abs(delta) * 0.22))
        away_prob_raw = max(0.05, 1.0 - home_prob_raw - draw_prob_raw)

        total = home_prob_raw + draw_prob_raw + away_prob_raw
        home_prob = home_prob_raw / total
        draw_prob = draw_prob_raw / total
        away_prob = away_prob_raw / total

        expected_home_goals = min(max(1.30 + delta * 1.05, 0.2), 3.8)
        expected_away_goals = min(max(1.15 - delta * 1.00, 0.2), 3.8)

        predicted_home_goals = int(round(expected_home_goals))
        predicted_away_goals = int(round(expected_away_goals))

        if home_prob >= away_prob and home_prob >= draw_prob:
            outcome = "home_win"
        elif away_prob >= home_prob and away_prob >= draw_prob:
            outcome = "away_win"
        else:
            outcome = "draw"

        confidence = max(home_prob, draw_prob, away_prob)

        return {
            "success": True,
            "model": "hybrid_processed_pyspark_plus_live_context",
            "fixture": {
                "id": fixture.get("id", fixture_id),
                "date": fixture.get("date"),
                "league": league.get("name"),
                "league_id": league_id,
                "season": season,
                "home": {"id": home_id, "name": home_name},
                "away": {"id": away_id, "name": away_name},
            },
            "prediction": {
                "outcome": outcome,
                "confidence": round(confidence, 4),
                "probabilities": {
                    "home_win": round(home_prob, 4),
                    "draw": round(draw_prob, 4),
                    "away_win": round(away_prob, 4),
                },
                "expected_goals": {
                    "home": round(expected_home_goals, 2),
                    "away": round(expected_away_goals, 2),
                },
                "predicted_score": {
                    "home": predicted_home_goals,
                    "away": predicted_away_goals,
                },
            },
            "signals": {
                "processed": {
                    "home": home_processed,
                    "away": away_processed,
                },
                "live_context": {
                    "home": home_live,
                    "away": away_live,
                },
                "final_strength": {
                    "home": round(home_strength, 4),
                    "away": round(away_strength, 4),
                    "delta_with_home_advantage": round(delta, 4),
                },
            },
        }

    def _build_team_index(self, team_stats) -> Dict[str, Dict[str, Any]]:
        index: Dict[str, Dict[str, Any]] = {}
        for row in team_stats:
            team_name = row.get("teamName")
            if not team_name:
                continue
            index[self._normalize_name(team_name)] = row
        return index

    def _compute_bounds(self, team_stats) -> Dict[str, Dict[str, float]]:
        if not team_stats:
            return {
                "shots_pm": {"min": 0.0, "max": 1.0},
                "passes_pm": {"min": 0.0, "max": 1.0},
                "fouls_pm": {"min": 0.0, "max": 1.0},
                "control": {"min": 0.0, "max": 1.0},
            }

        shots_pm_vals = []
        passes_pm_vals = []
        fouls_pm_vals = []
        control_vals = []

        for row in team_stats:
            matches = max(float(row.get("matches", 1) or 1), 1.0)
            total_events = max(float(row.get("total_events", 1) or 1), 1.0)
            shots_pm_vals.append(float(row.get("shots", 0) or 0) / matches)
            passes_pm_vals.append(float(row.get("passes", 0) or 0) / matches)
            fouls_pm_vals.append(float(row.get("fouls", 0) or 0) / matches)
            control_vals.append(float(row.get("passes", 0) or 0) / total_events)

        return {
            "shots_pm": {"min": min(shots_pm_vals), "max": max(shots_pm_vals)},
            "passes_pm": {"min": min(passes_pm_vals), "max": max(passes_pm_vals)},
            "fouls_pm": {"min": min(fouls_pm_vals), "max": max(fouls_pm_vals)},
            "control": {"min": min(control_vals), "max": max(control_vals)},
        }

    def _processed_strength(self, team_name: str) -> Dict[str, Any]:
        row = self.team_index.get(self._normalize_name(team_name))
        if not row:
            return {
                "team_name": team_name,
                "score": 0.5,
                "source": "processed_data_default",
                "matched": False,
            }

        matches = max(float(row.get("matches", 1) or 1), 1.0)
        total_events = max(float(row.get("total_events", 1) or 1), 1.0)

        shots_pm = float(row.get("shots", 0) or 0) / matches
        passes_pm = float(row.get("passes", 0) or 0) / matches
        fouls_pm = float(row.get("fouls", 0) or 0) / matches
        control = float(row.get("passes", 0) or 0) / total_events

        shots_n = self._minmax(shots_pm, "shots_pm")
        passes_n = self._minmax(passes_pm, "passes_pm")
        fouls_n = self._minmax(fouls_pm, "fouls_pm")
        control_n = self._minmax(control, "control")

        score = 0.44 * shots_n + 0.30 * passes_n + 0.18 * control_n + 0.08 * (1.0 - fouls_n)

        return {
            "team_name": team_name,
            "score": round(score, 4),
            "source": "processed_data",
            "matched": True,
            "features": {
                "shots_per_match": round(shots_pm, 4),
                "passes_per_match": round(passes_pm, 4),
                "fouls_per_match": round(fouls_pm, 4),
                "control_ratio": round(control, 4),
            },
        }

    def _live_strength(self, team_id: Optional[int], league_id: Optional[int], season: Optional[int]) -> Dict[str, Any]:
        if not team_id or not league_id or not season:
            return {
                "score": 0.5,
                "source": "live_context_default",
                "team_id": team_id,
            }

        team_stats_payload = self.live_service.get_team_stats(team=team_id, league=league_id, season=season)
        standings_payload = self.live_service.get_standings(league=league_id, season=season)

        wins_rate = 0.5
        goals_balance = 0.5
        shots_conv = 0.5
        points_per_game_n = 0.5

        if team_stats_payload.get("success") and team_stats_payload.get("data"):
            stats = team_stats_payload["data"][0]
            fixtures = stats.get("fixtures", {})
            played = max(float((fixtures.get("played") or {}).get("total", 0) or 0), 1.0)
            wins = float((fixtures.get("wins") or {}).get("total", 0) or 0)
            wins_rate = min(max(wins / played, 0.0), 1.0)

            goals_for = float((stats.get("goals") or {}).get("for", {}).get("total", {}).get("total", 0) or 0)
            goals_against = float((stats.get("goals") or {}).get("against", {}).get("total", {}).get("total", 0) or 0)
            goal_diff_pm = (goals_for - goals_against) / played
            goals_balance = min(max((goal_diff_pm + 2.0) / 4.0, 0.0), 1.0)

            shots_total = float((stats.get("shots") or {}).get("total", 0) or 0)
            shots_on = float((stats.get("shots") or {}).get("on", 0) or 0)
            shots_conv = min(max(shots_on / max(shots_total, 1.0), 0.0), 1.0)

        if standings_payload.get("success"):
            ppm = self._extract_points_per_match(standings_payload.get("data", []), team_id)
            if ppm is not None:
                points_per_game_n = min(max(ppm / 3.0, 0.0), 1.0)

        live_score = 0.40 * wins_rate + 0.25 * goals_balance + 0.20 * points_per_game_n + 0.15 * shots_conv

        return {
            "team_id": team_id,
            "score": round(live_score, 4),
            "source": "live_context",
            "features": {
                "wins_rate": round(wins_rate, 4),
                "goals_balance": round(goals_balance, 4),
                "shots_on_ratio": round(shots_conv, 4),
                "points_per_game_norm": round(points_per_game_n, 4),
            },
        }

    def _extract_points_per_match(self, standings_data, team_id: int) -> Optional[float]:
        for block in standings_data:
            league = block.get("league", {})
            for group in league.get("standings", []):
                for row in group:
                    team = row.get("team", {})
                    if int(team.get("id", -1)) != int(team_id):
                        continue
                    points = float(row.get("points", 0) or 0)
                    played = max(float((row.get("all") or {}).get("played", 0) or 0), 1.0)
                    return points / played
        return None

    def _minmax(self, value: float, field: str) -> float:
        min_val = self.bounds[field]["min"]
        max_val = self.bounds[field]["max"]
        if max_val <= min_val:
            return 0.5
        return (value - min_val) / (max_val - min_val)

    def _normalize_name(self, name: str) -> str:
        text = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
        return " ".join(text.lower().replace("&", "and").split())

    def _sigmoid(self, x: float) -> float:
        return 1.0 / (1.0 + math.exp(-x))
