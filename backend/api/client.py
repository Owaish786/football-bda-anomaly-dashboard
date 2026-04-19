"""
API Client for testing the Football BDA Backend
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"


class FootballAPIClient:
    """Client for interacting with Football BDA API"""
    
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
    
    def health_check(self):
        """Check API health"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def get_rankings(self, limit=20):
        """Get team rankings"""
        response = requests.get(f"{self.base_url}/rankings", params={'limit': limit})
        return response.json()
    
    def get_teams(self):
        """Get list of teams"""
        response = requests.get(f"{self.base_url}/teams")
        return response.json()
    
    def compare_teams(self, team1, team2):
        """Compare two teams"""
        payload = {'team1': team1, 'team2': team2}
        response = requests.post(f"{self.base_url}/teams/compare", json=payload)
        return response.json()
    
    def get_players(self, team=None):
        """Get list of players"""
        params = {'team': team} if team else {}
        response = requests.get(f"{self.base_url}/players", params=params)
        return response.json()
    
    def compare_players(self, player1, player2):
        """Compare two players"""
        payload = {'player1': player1, 'player2': player2}
        response = requests.post(f"{self.base_url}/players/compare", json=payload)
        return response.json()


if __name__ == "__main__":
    client = FootballAPIClient()
    
    # Test health
    print("🔍 Health Check:")
    print(json.dumps(client.health_check(), indent=2))
    
    # Test rankings
    print("\n📊 Team Rankings (Top 5):")
    rankings = client.get_rankings(limit=5)
    if rankings['success']:
        for team in rankings['data']:
            print(f"  {team['rank']}. {team['teamName']} - Score: {team['ranking_score']}")
    
    # Test teams list
    print("\n👥 Available Teams:")
    teams = client.get_teams()
    if teams['success']:
        for team in teams['data'][:5]:
            print(f"  - {team}")
    
    # Test team comparison
    print("\n⚔️ Team Comparison (Manchester City vs Liverpool):")
    comparison = client.compare_teams('Manchester City', 'Liverpool')
    if comparison['success']:
        print(json.dumps(comparison['data']['comparison'], indent=2))
    
    # Test players list
    print("\n👤 Available Players:")
    players = client.get_players()
    if players['success']:
        for player in players['data'][:5]:
            print(f"  - {player}")
    
    # Test player comparison
    print("\n⚔️ Player Comparison (Erling Haaland vs Harry Kane):")
    player_comp = client.compare_players('Erling Haaland', 'Harry Kane')
    if player_comp['success']:
        print(json.dumps(player_comp['data']['comparison'], indent=2))
