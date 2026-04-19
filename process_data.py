"""
Data Processing Job - Process CSV and export aggregated results
Run this to load real data from CSV and generate analytics
"""

import os
import sys
import json
from pathlib import Path

# Add the project to path
sys.path.insert(0, str(Path(__file__).parent))

def process_with_pyspark():
    """Process football data using PySpark"""
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col, count, sum as spark_sum, avg, when
    
    print("\n" + "="*60)
    print("Football BDA - Data Processing with PySpark")
    print("="*60)
    
    # Initialize Spark
    spark = SparkSession.builder \
        .appName("FootballDataProcessor") \
        .master("local[*]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    
    # Load data
    data_path = "./data/football_final_dataset.csv"
    
    if not os.path.exists(data_path):
        print(f"❌ Data file not found: {data_path}")
        return False
    
    print(f"\n📂 Loading data from: {data_path}")
    try:
        df = spark.read.csv(data_path, header=True, inferSchema=True)
        print(f"✓ Data loaded successfully")
        print(f"   Total rows: {df.count():,}")
        print(f"   Columns: {', '.join(df.columns)}")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False
    
    # Process teams
    print("\n📊 Processing teams...")
    try:
        teams = df.select("teamName").distinct().collect()
        teams_list = [row[0] for row in teams if row[0]]
        print(f"✓ Found {len(teams_list)} teams")
        
        # Get team stats
        team_stats = []
        for team in sorted(teams_list)[:10]:  # Top 10 for demo
            team_df = df.filter(col("teamName") == team)
            stats = {
                "teamName": team,
                "total_events": team_df.count(),
                "matches": team_df.select("matchId").distinct().count(),
                "passes": team_df.filter(col("eventName") == "Pass").count(),
                "shots": team_df.filter(col("eventName") == "Shot").count(),
                "fouls": team_df.filter(col("eventName") == "Foul").count(),
            }
            team_stats.append(stats)
            print(f"  {team}: {stats['total_events']} events")
    except Exception as e:
        print(f"⚠️  Error processing teams: {e}")
        team_stats = []
    
    # Process players
    print("\n👤 Processing players...")
    try:
        players = df.select("playerName").distinct().collect()
        players_list = [row[0] for row in players if row[0]]
        print(f"✓ Found {len(players_list)} players")
    except Exception as e:
        print(f"⚠️  Error processing players: {e}")
        players_list = []
    
    # Save results
    results = {
        "teams": teams_list,
        "players": players_list,
        "team_stats": team_stats,
        "total_rows": df.count(),
        "total_columns": len(df.columns)
    }
    
    output_file = "./data/processed_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_file}")
    print(f"   Teams: {len(teams_list)}")
    print(f"   Players: {len(players_list)}")
    
    spark.stop()
    return True


def process_without_pyspark():
    """Fallback: Process data without PySpark using pandas"""
    try:
        import pandas as pd
        
        print("\n" + "="*60)
        print("Football BDA - Data Processing with Pandas")
        print("="*60)
        
        data_path = "./data/football_final_dataset.csv"
        
        if not os.path.exists(data_path):
            print(f"❌ Data file not found: {data_path}")
            return False
        
        print(f"\n📂 Loading data from: {data_path}")
        df = pd.read_csv(data_path)
        print(f"✓ Data loaded successfully")
        print(f"   Total rows: {len(df):,}")
        print(f"   Columns: {', '.join(df.columns)}")
        
        # Process teams
        print("\n📊 Processing teams...")
        teams_list = df['teamName'].unique().tolist()
        print(f"✓ Found {len(teams_list)} teams")
        
        # Get team stats
        team_stats = []
        for team in sorted(teams_list)[:10]:  # Top 10 for demo
            team_df = df[df['teamName'] == team]
            stats = {
                "teamName": team,
                "total_events": len(team_df),
                "matches": team_df['matchId'].nunique(),
                "passes": len(team_df[team_df['eventName'] == 'Pass']),
                "shots": len(team_df[team_df['eventName'] == 'Shot']),
                "fouls": len(team_df[team_df['eventName'] == 'Foul']),
            }
            team_stats.append(stats)
            print(f"  {team}: {stats['total_events']} events")
        
        # Process players
        print("\n👤 Processing players...")
        players_list = df['playerName'].unique().tolist()
        print(f"✓ Found {len(players_list)} players")
        
        # Save results
        results = {
            "teams": teams_list,
            "players": players_list,
            "team_stats": team_stats,
            "total_rows": len(df),
            "total_columns": len(df.columns)
        }
        
        output_file = "./data/processed_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Results saved to: {output_file}")
        print(f"   Teams: {len(teams_list)}")
        print(f"   Players: {len(players_list)}")
        
        return True
        
    except ImportError:
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n🚀 Starting data processing job...")
    
    # Try PySpark first
    try:
        success = process_with_pyspark()
    except ImportError:
        print("\n⚠️  PySpark not available, falling back to Pandas...")
        success = process_without_pyspark()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n⚠️  Falling back to Pandas...")
        success = process_without_pyspark()
    
    if not success:
        print("\n❌ Data processing failed!")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ Data processing completed successfully!")
    print("="*60)
    print("\nYou can now:")
    print("  1. Run the API: python backend/api/app.py")
    print("  2. Test endpoints: curl http://localhost:5001/api/health")
    print("\n")
