# Hike Recommender 

An AI-powered hiking recommendation system that learns from your completed hikes to suggest new adventures tailored to your skill level and preferences.

## Features

- **Hike Logging**: Input details about hikes you've completed
- **Difficulty Analysis**: AI analyzes patterns in your hiking history
- **Smart Recommendations**: Get personalized hike suggestions based on your experience
- **Progressive Difficulty**: Recommendations adapt as your skills improve
- **User Dashboard**: Track your hiking statistics and progress

## Tech Stack

- **Backend**: Python Flask with SQLAlchemy
- **Frontend**: React with TypeScript
- **Database**: SQLite (development)
- **AI/ML**: scikit-learn for recommendation algorithms
- **Styling**: Custom CSS with responsive design

## Project Structure

```
hike-recommender/
├── backend/                 # Flask API server
│   ├── app.py              # Main Flask application
│   ├── models.py           # Database models
│   ├── recommendation_engine.py  # AI recommendation logic
│   ├── requirements.txt    # Python dependencies
│   └── venv/              # Virtual environment
├── frontend/               # React application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API service layer
│   │   ├── types.ts        # TypeScript interfaces
│   │   └── App.tsx         # Main app component
│   ├── package.json        # Node.js dependencies
│   └── public/            # Static assets
├── docs/                  # Documentation
│   └── data_model.md      # Database schema documentation
├── start_backend.sh       # Backend startup script
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.9+ 
- Node.js 16+
- npm or yarn

### 1. Set up the Backend

```bash
cd hike-recommender/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py
```

The backend will start at `http://localhost:5001` with sample hiking data already loaded.

### 2. Set up the Frontend

```bash
cd hike-recommender/frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will start at `http://localhost:3000` and automatically connect to the backend.

### 3. Using the Application

1. **Browse Hikes**: View all available hiking trails with difficulty ratings
2. **Log Completed Hikes**: Add hikes you've done with personal ratings and notes
3. **View Dashboard**: See your hiking statistics and recent activity
4. **Get Recommendations**: Receive AI-powered suggestions based on your history

## How the AI Works

The recommendation engine analyzes your hiking patterns including:

- **Distance Preferences**: Average and maximum distances you've completed
- **Elevation Comfort**: Your experience with different elevation gains
- **Difficulty Progression**: How your skill level has improved over time
- **Personal Ratings**: Which types of hikes you enjoyed most
- **Challenge Readiness**: When you're ready for the next difficulty level

The AI uses these factors to score potential hikes and provide explanations for each recommendation.

## Sample Data

The application comes with 5 sample hikes from Yosemite National Park:

- **Mirror Lake Loop** (Easy, 2.4 miles)
- **Sentinel Dome** (Easy-Moderate, 2.2 miles) 
- **Mist Trail to Vernal Fall** (Moderate, 5.5 miles)
- **Eagle Peak Trail** (Hard, 13.5 miles)
- **Half Dome** (Very Hard, 16.0 miles)

## API Endpoints

The backend provides a RESTful API:

- `GET /api/health` - Health check
- `GET /api/hikes` - Get all hikes
- `POST /api/hikes` - Create new hike
- `GET /api/completions?user_id=<id>` - Get user completions
- `POST /api/completions` - Log completed hike
- `GET /api/recommendations/<user_id>` - Get AI recommendations
- `GET /api/stats/<user_id>` - Get user statistics

## Testing

Test the backend API:

```bash
cd backend
source venv/bin/activate
pip install requests  # If not already installed
python test_app.py
```

## Development

### Adding New Hikes

You can add new hikes either through the frontend interface or directly via the API:

```bash
curl -X POST http://localhost:5001/api/hikes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mount Whitney",
    "location": "California, USA",
    "distance_miles": 22.0,
    "elevation_gain_feet": 6100,
    "difficulty_level": 5,
    "description": "Highest peak in contiguous US"
  }'
```

### Customizing the Recommendation Algorithm

The recommendation logic is in `backend/recommendation_engine.py`. You can modify:

- **Scoring weights** for different factors
- **Progression rules** for difficulty advancement
- **Similarity metrics** for comparing hikes
- **Confidence thresholds** for recommendations

## Troubleshooting

### Port 5000 in use
The backend uses port 5001 to avoid conflicts with macOS AirPlay. If you need to change it, update both `backend/app.py` and `frontend/src/services/api.ts`.

### Database issues
The SQLite database is created automatically. To reset it, delete `backend/hike_recommender.db` and restart the server.

### Frontend API errors
Ensure the backend is running on port 5001 before starting the frontend.

## Contributing

Feel free to contribute by:

- Adding new hiking trail data
- Improving the recommendation algorithm
- Enhancing the user interface
- Adding new features (weather integration, photos, etc.)
- Writing tests
- Improving documentation

## License

This project is open source and available under the MIT License.
