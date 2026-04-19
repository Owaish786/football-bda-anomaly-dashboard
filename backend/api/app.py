"""
Flask API for Football BDA Frontend
Provides REST endpoints for team/player analytics and rankings
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
import traceback
import sys
import threading

# Try to import PySpark components, fall back to mock data if not available
try:
    from backend.spark_jobs.data_processor import FootballDataProcessor
    from backend.services.analytics_service import AnalyticsServiceFactory, TeamAnalyticsService, PlayerAnalyticsService
    PYSPARK_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ PySpark not available: {e}")
    PYSPARK_AVAILABLE = False

from backend.services.data_provider import (
    get_teams_for_rankings as data_get_teams_for_rankings,
    get_team_comparison as data_get_team_comparison,
    get_player_comparison as data_get_player_comparison,
    get_teams_list as data_get_teams_list,
    get_players_list as data_get_players_list,
)
from backend.services.ml_service import detect_team_anomalies

load_dotenv()

app = Flask(__name__)
CORS(app)

# Global variables
processor = None
team_service = None
player_service = None
USE_MOCK_DATA = True  # Set to False when real data is ready
INIT_STATUS = 'pending'
INIT_ERROR = None
INIT_THREAD = None


def initialize_services():
    """Initialize Spark and services"""
    global processor, team_service, player_service, USE_MOCK_DATA, INIT_STATUS, INIT_ERROR
    INIT_STATUS = 'initializing'
    INIT_ERROR = None

    # If processed results are already present, serve real data immediately.
    # Spark initialization can continue in the background for full processing support.
    from backend.services.data_provider import REAL_DATA
    if REAL_DATA:
        USE_MOCK_DATA = False
    
    if not PYSPARK_AVAILABLE:
        print("⚠ PySpark not available, using processed data or mock data")
        
        # Check if real processed data exists
        if REAL_DATA:
            USE_MOCK_DATA = False
            INIT_STATUS = 'ready'
            print("✓ Real data loaded from processed results!")
        else:
            USE_MOCK_DATA = True
            INIT_STATUS = 'ready'
            print("⚠ Using mock data (no real data found)")
        return
    
    try:
        processor = FootballDataProcessor()
        data_path = os.getenv('DATA_PATH', './data')
        
        # Try to load real data
        if processor.load_data():
            USE_MOCK_DATA = False
            AnalyticsServiceFactory.initialize(processor)
            team_service = AnalyticsServiceFactory.get_team_service()
            player_service = AnalyticsServiceFactory.get_player_service()
            INIT_STATUS = 'ready'
            print("✓ Real data loaded successfully")
        else:
            print("⚠ Real data not found, using mock data")
            USE_MOCK_DATA = True
            INIT_STATUS = 'ready'
            
    except Exception as e:
        print(f"⚠ Error initializing Spark: {e}")
        print("Using mock data instead")
        USE_MOCK_DATA = True
        INIT_STATUS = 'error'
        INIT_ERROR = str(e)


def start_background_initialization():
    """Start initialization in a daemon thread so API can answer health checks immediately."""
    global INIT_THREAD
    if INIT_THREAD and INIT_THREAD.is_alive():
        return
    INIT_THREAD = threading.Thread(target=initialize_services, daemon=True)
    INIT_THREAD.start()


# ============== HEALTH CHECK ENDPOINTS ==============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'football-bda-api',
        'using_mock_data': USE_MOCK_DATA,
        'initialization_status': INIT_STATUS,
        'initialization_error': INIT_ERROR,
    }), 200


# ============== TEAM RANKING ENDPOINTS ==============

@app.route('/api/rankings', methods=['GET'])
def get_rankings():
    """
    Get team rankings
    Query params: limit (default: 20)
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        
        # Always use mock_data functions - they handle both real and mock data
        rankings = data_get_teams_for_rankings()
        if rankings:
            rankings = rankings[:limit]
        
        return jsonify({
            'success': True,
            'data': rankings,
            'count': len(rankings) if rankings else 0
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


# ============== TEAM COMPARISON ENDPOINTS ==============

@app.route('/api/teams', methods=['GET'])
def get_teams_list_endpoint():
    """Get list of all teams"""
    try:
        # Always use mock_data functions - they handle both real and mock data
        teams = data_get_teams_list()
        
        return jsonify({
            'success': True,
            'data': teams,
            'count': len(teams) if teams else 0
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/teams/compare', methods=['POST'])
def compare_teams():
    """
    Compare two teams
    POST body: {"team1": "TeamName1", "team2": "TeamName2"}
    """
    try:
        data = request.get_json()
        team1 = data.get('team1')
        team2 = data.get('team2')
        
        if not team1 or not team2:
            return jsonify({
                'success': False,
                'error': 'Missing team1 or team2 in request'
            }), 400
        
        # Always use mock_data functions - they handle both real and mock data
        comparison = data_get_team_comparison(team1, team2)
        
        return jsonify({
            'success': True,
            'data': comparison
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


# ============== PLAYER COMPARISON ENDPOINTS ==============

@app.route('/api/players', methods=['GET'])
def get_players_list_endpoint():
    """Get list of all players, optionally filtered by team"""
    try:
        team = request.args.get('team', None)
        
        # Always use mock_data functions - they handle both real and mock data
        players = data_get_players_list(team)
        
        return jsonify({
            'success': True,
            'data': players,
            'count': len(players) if players else 0,
            'filtered_by_team': team
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/players/compare', methods=['POST'])
def compare_players():
    """
    Compare two players
    POST body: {"player1": "PlayerName1", "player2": "PlayerName2"}
    """
    try:
        data = request.get_json()
        player1 = data.get('player1')
        player2 = data.get('player2')
        
        if not player1 or not player2:
            return jsonify({
                'success': False,
                'error': 'Missing player1 or player2 in request'
            }), 400
        
        # Always use mock_data functions - they handle both real and mock data
        comparison = data_get_player_comparison(player1, player2)
        
        return jsonify({
            'success': True,
            'data': comparison
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


# ============== ML ENDPOINTS ==============

@app.route('/api/anomalies/teams', methods=['GET'])
def team_anomalies():
    """Detect team anomalies using IsolationForest."""
    try:
        contamination = request.args.get('contamination', 0.2, type=float)
        top_n = request.args.get('top_n', 5, type=int)

        result = detect_team_anomalies(contamination=contamination, top_n=top_n)
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


# ============== ERROR HANDLERS ==============

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'path': request.path
    }), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


# ============== STARTUP ==============

if __name__ == '__main__':
    print("=" * 50)
    print("Football BDA Backend API")
    print("=" * 50)
    
    # Initialize services in background so startup remains responsive
    start_background_initialization()
    
    # Start Flask app
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('API_DEBUG', 'True').lower() == 'true'
    
    print(f"\n📢 Starting API on {host}:{port}")
    print(f"🔄 Debug mode: {debug}")
    print(f"📊 Using mock data: {USE_MOCK_DATA}\n")
    
    app.run(host=host, port=port, debug=debug)
