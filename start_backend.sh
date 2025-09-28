#!/bin/bash

echo "🥾 Starting Hike Recommender Backend..."

cd backend

# Activate virtual environment
source venv/bin/activate

# Start the Flask application
echo "Starting Flask server on http://localhost:5001"
python app.py