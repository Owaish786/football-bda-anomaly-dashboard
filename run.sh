#!/bin/bash

# Football BDA Backend - Quick Start Script

set -e

echo "================================"
echo "Football BDA Backend Setup"
echo "================================"

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "✓ Docker found"
    
    # Ask user preference
    read -p "Do you want to run with Docker? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🐳 Starting Docker services..."
        docker-compose up --build
        exit 0
    fi
fi

echo "🐍 Running locally..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

echo "✓ Python 3 found"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check for data
if [ ! -f "data/football_final_dataset.csv" ]; then
    echo "⚠️  Data file not found, using mock data"
fi

# Run the API
echo "🚀 Starting API..."
python backend/api/app.py
