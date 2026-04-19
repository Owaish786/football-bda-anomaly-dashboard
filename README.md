# Football BDA Backend - Setup & Usage Guide

## 📋 Overview

This backend provides REST APIs for football analytics, including:
- **Team Rankings** - Rank teams by performance metrics
- **Team Comparison** - Compare two teams side-by-side
- **Player Comparison** - Compare two players side-by-side

## 🏗️ Architecture

```
football_bda/
├── backend/
│   ├── api/              # Flask REST API
│   │   ├── app.py        # Main Flask application
│   │   └── client.py     # API client for testing
│   ├── spark_jobs/       # PySpark data processing
│   │   └── data_processor.py
│   └── services/         # Business logic layer
│       ├── analytics_service.py
│       └── mock_data.py
├── data/                 # Data directory
├── docker-compose.yml    # Docker orchestration
├── Dockerfile            # Container configuration
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables
```

## 🚀 Quick Start (3 Options)

### Option 1: Docker (Recommended for Production)

```bash
cd football_bda

# Build and start all services
docker-compose up --build

# API will be available at http://localhost:5000
```

### Option 2: Local Development (No Docker)

```bash
cd football_bda

# Install dependencies
pip install -r requirements.txt

# Add your data to ./data/ folder
# Copy your CSV file: football_final_dataset.csv

# Run the API
python backend/api/app.py

# API will be available at http://localhost:5000
```

### Option 3: PySpark Only (Data Processing)

```bash
cd football_bda

# Install PySpark
pip install pyspark pandas numpy

# Run data processor
python backend/spark_jobs/data_processor.py
```

## 📊 Data Setup

### Real Data
Place your CSV file in the `data/` folder:
```
football_bda/data/football_final_dataset.csv
```

Expected CSV columns:
- `matchId` - Match identifier
- `teamId` - Team identifier
- `teamName` - Team name
- `playerId` - Player identifier
- `playerName` - Player name
- `eventName` - Event type (Pass, Shot, Foul, Tackle, etc.)
- `subEventName` - Event subtype
- `minute` - Match minute
- `x` - X coordinate
- `y` - Y coordinate

### Mock Data
If no CSV is found, the backend automatically uses mock data for testing.

## 🔌 API Endpoints

### 1. Health Check
```bash
GET /api/health
```
Response:
```json
{
  "status": "healthy",
  "service": "football-bda-api",
  "using_mock_data": true
}
```

### 2. Get Team Rankings
```bash
GET /api/rankings?limit=20
```
Response:
```json
{
  "success": true,
  "data": [
    {
      "rank": 1,
      "teamName": "Manchester City",
      "ranking_score": 95.5,
      "total_matches": 38,
      "shots": 1250,
      "passes": 28500,
      "pass_accuracy": 87.5
    }
  ]
}
```

### 3. Get Teams List
```bash
GET /api/teams
```

### 4. Compare Teams
```bash
POST /api/teams/compare
Content-Type: application/json

{
  "team1": "Manchester City",
  "team2": "Liverpool"
}
```

### 5. Get Players List
```bash
GET /api/players?team=Manchester City
```

### 6. Compare Players
```bash
POST /api/players/compare
Content-Type: application/json

{
  "player1": "Erling Haaland",
  "player2": "Harry Kane"
}
```

## 🧪 Testing the API

### Using the Python Client
```bash
cd football_bda
python backend/api/client.py
```

### Using cURL
```bash
# Health check
curl http://localhost:5000/api/health

# Get rankings
curl http://localhost:5000/api/rankings?limit=10

# Get teams
curl http://localhost:5000/api/teams

# Compare teams
curl -X POST http://localhost:5000/api/teams/compare \
  -H "Content-Type: application/json" \
  -d '{"team1":"Manchester City","team2":"Liverpool"}'
```

### Using Python Requests
```python
import requests

# Get rankings
response = requests.get('http://localhost:5000/api/rankings?limit=20')
print(response.json())

# Compare teams
response = requests.post(
    'http://localhost:5000/api/teams/compare',
    json={'team1': 'Manchester City', 'team2': 'Liverpool'}
)
print(response.json())
```

## 📝 Configuration

Edit `.env` file to customize:
```env
# Spark Configuration
SPARK_MASTER=spark://localhost:7077
SPARK_LOCAL_IP=127.0.0.1

# Data Configuration
DATA_PATH=./data
HDFS_PATH=hdfs://namenode:9000/user/spark/football_data/

# API Configuration
FLASK_ENV=development
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=True
```

## 🐳 Docker Services

### Spark Master
- Web UI: http://localhost:8080
- Port: 7077

### Spark Worker
- Web UI: http://localhost:8081

### API Service
- Endpoint: http://localhost:5000
- Container: football-api

## 🔗 Integration with Frontend

The frontend can fetch data using:

```python
# Python (Streamlit)
import requests

response = requests.get('http://localhost:5000/api/rankings?limit=20')
teams = response.json()['data']

# Display in Streamlit
import streamlit as st
st.dataframe(teams)
```

## 🛠️ Troubleshooting

### Issue: Data not loading
```bash
# Check if CSV exists
ls -la data/

# Check logs
docker logs football-api

# Use mock data (automatic fallback)
```

### Issue: Port already in use
```bash
# Change port in .env
API_PORT=5001

# Or kill existing process
lsof -ti:5000 | xargs kill -9
```

### Issue: Spark connection error
```bash
# Check Docker containers
docker ps

# Restart services
docker-compose restart

# Check logs
docker logs spark-master
```

## 📈 Scaling

For larger datasets:

1. **Increase Spark memory** in `docker-compose.yml`:
   ```yaml
   environment:
     - SPARK_WORKER_MEMORY=4G
     - SPARK_WORKER_CORES=4
   ```

2. **Use HDFS path** in `.env`:
   ```env
   DATA_PATH=hdfs://namenode:9000/user/spark/football_data/
   ```

3. **Add more workers**:
   ```yaml
   services:
     spark-worker-2:
       # Copy spark-worker config
   ```

## 📚 References

- [PySpark Documentation](https://spark.apache.org/docs/latest/api/python/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Apache Spark](https://spark.apache.org/)

---

**Ready for production?** Contact the data team to set up HDFS integration and real data pipeline.
