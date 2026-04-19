"""
Live football data service powered by API-Football (api-sports.io).
"""

import os
from datetime import date
from typing import Any, Dict, Optional

import requests


class LiveFootballService:
    """Thin API client for API-Football endpoints."""

    def __init__(self) -> None:
        self.base_url = os.getenv("LIVE_API_BASE_URL", "https://v3.football.api-sports.io")
        self.timeout = int(os.getenv("LIVE_API_TIMEOUT", "12"))

        api_key = os.getenv("FOOTBALL_API_KEY", "").strip()
        api_host = os.getenv("FOOTBALL_API_HOST", "v3.football.api-sports.io")

        self.headers = {
            "x-apisports-key": api_key,
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": api_host,
        }

    @property
    def is_configured(self) -> bool:
        return bool(self.headers.get("x-apisports-key"))

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.is_configured:
            return {
                "success": False,
                "error": "FOOTBALL_API_KEY is not configured",
                "endpoint": endpoint,
                "data": [],
            }

        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params or {},
                timeout=self.timeout,
            )
            payload = response.json()

            if response.status_code != 200:
                return {
                    "success": False,
                    "error": payload.get("errors") or payload.get("message") or "Live API request failed",
                    "status_code": response.status_code,
                    "endpoint": endpoint,
                    "params": params or {},
                    "raw": payload,
                }

            return {
                "success": True,
                "endpoint": endpoint,
                "params": params or {},
                "results": payload.get("results", 0),
                "errors": payload.get("errors", []),
                "data": payload.get("response", []),
                "paging": payload.get("paging", {}),
            }
        except requests.RequestException as exc:
            return {
                "success": False,
                "error": str(exc),
                "endpoint": endpoint,
                "params": params or {},
                "data": [],
            }

    def get_live_scores(self, league: Optional[int] = None, season: Optional[int] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {"live": "all"}
        if league:
            params["league"] = int(league)
        if season:
            params["season"] = int(season)
        return self._get("/fixtures", params=params)

    def get_fixtures(
        self,
        league: Optional[int] = None,
        season: Optional[int] = None,
        team: Optional[int] = None,
        fixture_date: Optional[str] = None,
        next_n: Optional[int] = None,
        last_n: Optional[int] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if league:
            params["league"] = int(league)
        if season:
            params["season"] = int(season)
        if team:
            params["team"] = int(team)
        if fixture_date:
            params["date"] = fixture_date
        if next_n:
            params["next"] = int(next_n)
        if last_n:
            params["last"] = int(last_n)

        if not params:
            params["date"] = date.today().isoformat()

        return self._get("/fixtures", params=params)

    def get_standings(self, league: int, season: int) -> Dict[str, Any]:
        return self._get("/standings", params={"league": int(league), "season": int(season)})

    def get_team_stats(self, team: int, league: int, season: int) -> Dict[str, Any]:
        return self._get(
            "/teams/statistics",
            params={"team": int(team), "league": int(league), "season": int(season)},
        )

    def get_player_stats(
        self,
        team: int,
        season: int,
        league: Optional[int] = None,
        page: int = 1,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "team": int(team),
            "season": int(season),
            "page": int(page),
        }
        if league:
            params["league"] = int(league)
        return self._get("/players", params=params)

    def get_match_events(self, fixture: int) -> Dict[str, Any]:
        return self._get("/fixtures/events", params={"fixture": int(fixture)})

    def get_prediction(self, fixture: int) -> Dict[str, Any]:
        return self._get("/predictions", params={"fixture": int(fixture)})

    def get_fixture_by_id(self, fixture: int) -> Dict[str, Any]:
        return self._get("/fixtures", params={"id": int(fixture)})
