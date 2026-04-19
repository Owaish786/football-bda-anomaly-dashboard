"""
PySpark Data Processor for Football Analytics
Handles loading, processing, and aggregating football event data
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum as spark_sum, avg, max as spark_max, when, desc, row_number
from pyspark.sql.window import Window
import os
from dotenv import load_dotenv

load_dotenv()


class FootballDataProcessor:
    """Main data processor class for football analytics"""
    
    def __init__(self, spark_master=None, data_path=None):
        """Initialize Spark session"""
        self.spark_master = spark_master or os.getenv('SPARK_MASTER', 'local[*]')
        self.data_path = data_path or os.getenv('DATA_PATH', './data')
        
        self.spark = SparkSession.builder \
            .appName("FootballBDA") \
            .master(self.spark_master) \
            .config("spark.driver.memory", "2g") \
            .config("spark.executor.memory", "2g") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("ERROR")
        self.events_df = None
    
    def load_data(self, csv_file="football_final_dataset.csv"):
        """Load football events data from CSV"""
        file_path = os.path.join(self.data_path, csv_file)
        
        if os.path.exists(file_path):
            print(f"Loading data from {file_path}")
            self.events_df = self.spark.read.csv(file_path, header=True, inferSchema=True)
            print(f"Data loaded successfully. Total rows: {self.events_df.count()}")
            return self.events_df
        else:
            print(f"File not found: {file_path}")
            return None
    
    def get_team_rankings(self):
        """
        Calculate team rankings based on:
        - Win percentage
        - Goals scored
        - Recent performance
        """
        if self.events_df is None:
            return None
        
        # Group by team and calculate metrics
        team_stats = self.events_df.groupBy("teamName").agg(
            count("matchId").alias("total_matches"),
            spark_sum(when(col("eventName") == "Shot", 1).otherwise(0)).alias("shots"),
            spark_sum(when(col("eventName") == "Pass", 1).otherwise(0)).alias("passes"),
            spark_sum(when(col("eventName") == "Foul", 1).otherwise(0)).alias("fouls"),
            avg("x").alias("avg_x"),
            avg("y").alias("avg_y")
        ).distinct()
        
        # Calculate pass accuracy (successful passes / total passes)
        team_stats = team_stats.withColumn(
            "pass_accuracy",
            (col("passes") / (col("passes") + col("fouls") + 1)).cast("double")
        )
        
        # Calculate ranking score (normalized)
        team_stats = team_stats.withColumn(
            "ranking_score",
            (col("shots") * 10 + col("passes") * 0.1 + col("pass_accuracy") * 100) / col("total_matches")
        )
        
        # Order by ranking score
        rankings = team_stats.orderBy(desc("ranking_score"))
        
        return rankings
    
    def get_team_comparison(self, team1, team2):
        """
        Compare two teams
        Returns stats for both teams side by side
        """
        if self.events_df is None:
            return None, None
        
        # Filter data for both teams
        team1_df = self.events_df.filter(col("teamName") == team1)
        team2_df = self.events_df.filter(col("teamName") == team2)
        
        # Calculate stats for team1
        team1_stats = {
            "teamName": team1,
            "total_events": team1_df.count(),
            "total_matches": team1_df.select("matchId").distinct().count(),
            "passes": team1_df.filter(col("eventName") == "Pass").count(),
            "shots": team1_df.filter(col("eventName") == "Shot").count(),
            "fouls": team1_df.filter(col("eventName") == "Foul").count(),
            "tackles": team1_df.filter(col("eventName") == "Tackle").count(),
            "passes_success_rate": self._calculate_pass_accuracy(team1_df)
        }
        
        # Calculate stats for team2
        team2_stats = {
            "teamName": team2,
            "total_events": team2_df.count(),
            "total_matches": team2_df.select("matchId").distinct().count(),
            "passes": team2_df.filter(col("eventName") == "Pass").count(),
            "shots": team2_df.filter(col("eventName") == "Shot").count(),
            "fouls": team2_df.filter(col("eventName") == "Foul").count(),
            "tackles": team2_df.filter(col("eventName") == "Tackle").count(),
            "passes_success_rate": self._calculate_pass_accuracy(team2_df)
        }
        
        return team1_stats, team2_stats
    
    def get_player_comparison(self, player1, player2):
        """
        Compare two players
        Returns detailed stats for comparison
        """
        if self.events_df is None:
            return None, None
        
        # Filter data for both players
        player1_df = self.events_df.filter(col("playerName") == player1)
        player2_df = self.events_df.filter(col("playerName") == player2)
        
        # Calculate stats for player1
        player1_stats = {
            "playerName": player1,
            "team": player1_df.select("teamName").distinct().collect()[0][0] if player1_df.count() > 0 else "Unknown",
            "total_events": player1_df.count(),
            "passes": player1_df.filter(col("eventName") == "Pass").count(),
            "shots": player1_df.filter(col("eventName") == "Shot").count(),
            "fouls": player1_df.filter(col("eventName") == "Foul").count(),
            "tackles": player1_df.filter(col("eventName") == "Tackle").count(),
            "interceptions": player1_df.filter(col("eventName") == "Interception").count(),
            "avg_event_minute": float(player1_df.select(avg("minute")).collect()[0][0] or 0)
        }
        
        # Calculate stats for player2
        player2_stats = {
            "playerName": player2,
            "team": player2_df.select("teamName").distinct().collect()[0][0] if player2_df.count() > 0 else "Unknown",
            "total_events": player2_df.count(),
            "passes": player2_df.filter(col("eventName") == "Pass").count(),
            "shots": player2_df.filter(col("eventName") == "Shot").count(),
            "fouls": player2_df.filter(col("eventName") == "Foul").count(),
            "tackles": player2_df.filter(col("eventName") == "Tackle").count(),
            "interceptions": player2_df.filter(col("eventName") == "Interception").count(),
            "avg_event_minute": float(player2_df.select(avg("minute")).collect()[0][0] or 0)
        }
        
        return player1_stats, player2_stats
    
    def get_all_teams(self):
        """Get list of all unique teams"""
        if self.events_df is None:
            return []
        
        teams = self.events_df.select("teamName").distinct().collect()
        return [row[0] for row in teams if row[0]]
    
    def get_all_players(self, team=None):
        """Get list of all unique players, optionally filtered by team"""
        if self.events_df is None:
            return []
        
        if team:
            players = self.events_df.filter(col("teamName") == team).select("playerName").distinct().collect()
        else:
            players = self.events_df.select("playerName").distinct().collect()
        
        return [row[0] for row in players if row[0]]
    
    def _calculate_pass_accuracy(self, df):
        """Helper method to calculate pass accuracy"""
        total_passes = df.filter(col("eventName") == "Pass").count()
        if total_passes == 0:
            return 0.0
        
        # Approximate success rate (could be enhanced with actual data)
        successful_passes = df.filter(
            (col("eventName") == "Pass") & 
            (col("subEventName").like("%success%") | col("subEventName").isNull())
        ).count()
        
        return round((successful_passes / total_passes) * 100, 2)
    
    def stop(self):
        """Stop Spark session"""
        self.spark.stop()


if __name__ == "__main__":
    processor = FootballDataProcessor()
    processor.load_data()
    
    # Get all teams
    teams = processor.get_all_teams()
    print(f"\nTeams in dataset: {teams}")
    
    # Get rankings
    rankings = processor.get_team_rankings()
    if rankings:
        print("\nTop 10 Team Rankings:")
        rankings.limit(10).show()
    
    processor.stop()
