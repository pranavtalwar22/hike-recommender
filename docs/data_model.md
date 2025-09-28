# Data Model Design

## Core Entities

### Hikes Table
Stores information about available hiking trails.

```sql
CREATE TABLE hikes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    location VARCHAR(200) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    distance_miles DECIMAL(5, 2) NOT NULL,
    elevation_gain_feet INTEGER NOT NULL,
    estimated_duration_hours DECIMAL(3, 1),
    difficulty_level INTEGER NOT NULL CHECK (difficulty_level >= 1 AND difficulty_level <= 5),
    trail_type VARCHAR(50), -- 'loop', 'out-and-back', 'point-to-point'
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### User Completions Table
Tracks hikes completed by users with their personal ratings and experience.

```sql
CREATE TABLE user_completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hike_id INTEGER NOT NULL,
    user_id VARCHAR(100) NOT NULL, -- Simple user identification
    completed_date DATE NOT NULL,
    personal_rating INTEGER CHECK (personal_rating >= 1 AND personal_rating <= 5),
    actual_duration_hours DECIMAL(3, 1),
    weather_conditions VARCHAR(100),
    notes TEXT,
    difficulty_felt INTEGER CHECK (difficulty_felt >= 1 AND difficulty_felt <= 5),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hike_id) REFERENCES hikes(id)
);
```

### Recommendations Table
Stores AI-generated recommendations for users.

```sql
CREATE TABLE recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(100) NOT NULL,
    hike_id INTEGER NOT NULL,
    confidence_score DECIMAL(3, 2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    recommendation_reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_viewed BOOLEAN DEFAULT FALSE,
    is_accepted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (hike_id) REFERENCES hikes(id)
);
```

### User Preferences Table (Optional)
Stores user preferences for better recommendations.

```sql
CREATE TABLE user_preferences (
    user_id VARCHAR(100) PRIMARY KEY,
    preferred_distance_min DECIMAL(5, 2),
    preferred_distance_max DECIMAL(5, 2),
    preferred_elevation_min INTEGER,
    preferred_elevation_max INTEGER,
    preferred_regions TEXT, -- JSON array of preferred locations
    avoid_regions TEXT, -- JSON array of regions to avoid
    fitness_level INTEGER CHECK (fitness_level >= 1 AND fitness_level <= 5),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Difficulty Calculation Factors

The AI will consider these factors when analyzing difficulty:

1. **Distance** (miles)
2. **Elevation Gain** (feet)
3. **Trail Type** (loop vs out-and-back)
4. **User's Historical Performance**
5. **Personal Ratings vs Objective Difficulty**

## Recommendation Algorithm Inputs

- User's completed hikes (distance, elevation, difficulty ratings)
- Personal vs objective difficulty discrepancies
- Progression patterns (how user difficulty tolerance has changed)
- Seasonal preferences (if date patterns emerge)
- Location preferences

## Sample Data Structure

```python
# Sample hike record
{
    "id": 1,
    "name": "Mount Washington via Tuckerman Ravine",
    "location": "New Hampshire, USA",
    "distance_miles": 8.4,
    "elevation_gain_feet": 4250,
    "difficulty_level": 5,
    "trail_type": "out-and-back"
}

# Sample user completion
{
    "hike_id": 1,
    "user_id": "user123",
    "completed_date": "2024-07-15",
    "personal_rating": 4,
    "difficulty_felt": 5,
    "notes": "Challenging but rewarding. Great views at the summit."
}
```