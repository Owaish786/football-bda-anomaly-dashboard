"""
Service layer for Football Analytics
Handles business logic and data aggregation
"""

from backend.spark_jobs.data_processor import FootballDataProcessor


class TeamAnalyticsService:
    """Service for team-related analytics"""
    
    def __init__(self, processor):
        self.processor = processor
    
    def get_rankings(self, limit=20):
        """Get team rankings with limit"""
        rankings = self.processor.get_team_rankings()
        if rankings:
            data = rankings.limit(limit).toPandas().to_dict('records')
            return [{
                'rank': idx + 1,
                'teamName': row['teamName'],
                'ranking_score': round(row['ranking_score'], 2),
                'total_matches': int(row['total_matches']),
                'shots': int(row['shots']),
                'passes': int(row['passes']),
                'pass_accuracy': round(row['pass_accuracy'], 2)
            } for idx, row in enumerate(data)]
        return []
    
    def compare_teams(self, team1, team2):
        """Compare two teams"""
        stats1, stats2 = self.processor.get_team_comparison(team1, team2)
        
        return {
            'team1': stats1,
            'team2': stats2,
            'comparison': {
                'events_diff': stats1['total_events'] - stats2['total_events'],
                'passes_diff': stats1['passes'] - stats2['passes'],
                'shots_diff': stats1['shots'] - stats2['shots'],
                'pass_accuracy_diff': round(stats1['passes_success_rate'] - stats2['passes_success_rate'], 2)
            }
        }
    
    def get_teams_list(self):
        """Get list of all teams"""
        return self.processor.get_all_teams()


class PlayerAnalyticsService:
    """Service for player-related analytics"""
    
    def __init__(self, processor):
        self.processor = processor
    
    def compare_players(self, player1, player2):
        """Compare two players"""
        stats1, stats2 = self.processor.get_player_comparison(player1, player2)
        
        return {
            'player1': stats1,
            'player2': stats2,
            'comparison': {
                'events_diff': stats1['total_events'] - stats2['total_events'],
                'passes_diff': stats1['passes'] - stats2['passes'],
                'shots_diff': stats1['shots'] - stats2['shots'],
                'tackles_diff': stats1['tackles'] - stats2['tackles']
            }
        }
    
    def get_players_list(self, team=None):
        """Get list of all players, optionally by team"""
        return self.processor.get_all_players(team)
    
    def get_top_performers(self, metric='total_events', limit=10):
        """Get top performers by metric"""
        # This would need implementation in data_processor
        pass


class AnalyticsServiceFactory:
    """Factory to manage services"""
    
    _processor = None
    _team_service = None
    _player_service = None
    
    @classmethod
    def initialize(cls, processor):
        """Initialize all services with processor"""
        cls._processor = processor
        cls._team_service = TeamAnalyticsService(processor)
        cls._player_service = PlayerAnalyticsService(processor)
    
    @classmethod
    def get_team_service(cls):
        """Get team analytics service"""
        return cls._team_service
    
    @classmethod
    def get_player_service(cls):
        """Get player analytics service"""
        return cls._player_service
    
    @classmethod
    def get_processor(cls):
        """Get data processor"""
        return cls._processor
