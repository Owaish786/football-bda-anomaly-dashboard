# Football BDA Backend - Makefile

.PHONY: help install run docker-up docker-down test clean

help:
	@echo "Football BDA Backend - Available Commands"
	@echo "=========================================="
	@echo "make install         - Install dependencies"
	@echo "make run             - Run API locally"
	@echo "make docker-up       - Start Docker containers"
	@echo "make docker-down     - Stop Docker containers"
	@echo "make test            - Test API endpoints"
	@echo "make spark-process   - Run PySpark processor"
	@echo "make clean           - Clean cache files"
	@echo "make logs            - Show Docker logs"

install:
	pip install -r requirements.txt

run:
	python backend/api/app.py

docker-up:
	docker-compose up --build -d
	@echo "✓ Services started. API: http://localhost:5000"

docker-down:
	docker-compose down

docker-restart:
	docker-compose restart

test:
	python backend/api/client.py

spark-process:
	python backend/spark_jobs/data_processor.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete

logs:
	docker-compose logs -f api-service

logs-spark:
	docker-compose logs -f spark-master

env:
	cat .env

ps:
	docker-compose ps

status:
	@echo "Checking API health..."
	@curl -s http://localhost:5000/api/health | python -m json.tool || echo "API not running"
