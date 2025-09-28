from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, date
from models import db, Hike, UserCompletion, Recommendation, UserPreference
from recommendation_engine import RecommendationEngine
import os
import json

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///hike_recommender.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Initialize recommendation engine
recommender = RecommendationEngine()

def init_db():
    db.create_all()
    # Add some sample data if database is empty
    if Hike.query.count() == 0:
        add_sample_data()

def add_sample_data():
    """Add sample hiking data for testing"""
    sample_hikes = [
        {
            'name': 'Eagle Peak Trail',
            'location': 'Yosemite National Park, CA',
            'distance_miles': 13.5,
            'elevation_gain_feet': 2000,
            'difficulty_level': 4,
            'trail_type': 'out-and-back',
            'description': 'Challenging hike with spectacular views of Yosemite Valley.'
        },
        {
            'name': 'Mirror Lake Loop',
            'location': 'Yosemite National Park, CA',
            'distance_miles': 2.4,
            'elevation_gain_feet': 100,
            'difficulty_level': 1,
            'trail_type': 'loop',
            'description': 'Easy family-friendly walk around Mirror Lake.'
        },
        {
            'name': 'Half Dome',
            'location': 'Yosemite National Park, CA',
            'distance_miles': 16.0,
            'elevation_gain_feet': 4800,
            'difficulty_level': 5,
            'trail_type': 'out-and-back',
            'description': 'Iconic and strenuous hike requiring permits and cables.'
        },
        {
            'name': 'Mist Trail to Vernal Fall',
            'location': 'Yosemite National Park, CA',
            'distance_miles': 5.5,
            'elevation_gain_feet': 1000,
            'difficulty_level': 3,
            'trail_type': 'out-and-back',
            'description': 'Popular trail with beautiful waterfall views.'
        },
        {
            'name': 'Sentinal Dome',
            'location': 'Yosemite National Park, CA',
            'distance_miles': 2.2,
            'elevation_gain_feet': 400,
            'difficulty_level': 2,
            'trail_type': 'out-and-back',
            'description': 'Short hike to panoramic views of Yosemite Valley.'
        }
    ]
    
    for hike_data in sample_hikes:
        hike = Hike(**hike_data)
        db.session.add(hike)
    
    db.session.commit()
    print("Sample data added successfully!")

# API Routes

@app.route('/api/hikes', methods=['GET'])
def get_hikes():
    """Get all available hikes"""
    hikes = Hike.query.all()
    return jsonify([hike.to_dict() for hike in hikes])

@app.route('/api/hikes', methods=['POST'])
def create_hike():
    """Create a new hike"""
    data = request.get_json()
    
    try:
        hike = Hike(
            name=data['name'],
            location=data['location'],
            distance_miles=data['distance_miles'],
            elevation_gain_feet=data['elevation_gain_feet'],
            difficulty_level=data['difficulty_level'],
            trail_type=data.get('trail_type'),
            description=data.get('description'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            estimated_duration_hours=data.get('estimated_duration_hours')
        )
        
        db.session.add(hike)
        db.session.commit()
        
        return jsonify(hike.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/completions', methods=['GET'])
def get_user_completions():
    """Get all completions for a user"""
    user_id = request.args.get('user_id', 'default_user')
    completions = UserCompletion.query.filter_by(user_id=user_id).all()
    return jsonify([completion.to_dict() for completion in completions])

@app.route('/api/completions', methods=['POST'])
def add_completion():
    """Add a completed hike for a user"""
    data = request.get_json()
    
    try:
        completion = UserCompletion(
            hike_id=data['hike_id'],
            user_id=data.get('user_id', 'default_user'),
            completed_date=datetime.strptime(data['completed_date'], '%Y-%m-%d').date(),
            personal_rating=data.get('personal_rating'),
            actual_duration_hours=data.get('actual_duration_hours'),
            weather_conditions=data.get('weather_conditions'),
            notes=data.get('notes'),
            difficulty_felt=data.get('difficulty_felt')
        )
        
        db.session.add(completion)
        db.session.commit()
        
        return jsonify(completion.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/recommendations/<user_id>', methods=['GET'])
def get_recommendations(user_id):
    """Get AI-generated recommendations for a user"""
    try:
        # Get user's completed hikes
        completions = UserCompletion.query.filter_by(user_id=user_id).all()
        
        if not completions:
            return jsonify({'message': 'No completed hikes found. Add some hikes first to get recommendations!'}), 200
        
        # Generate new recommendations
        recommendations = recommender.generate_recommendations(user_id, completions)
        
        # Save recommendations to database
        for rec_data in recommendations:
            existing = Recommendation.query.filter_by(
                user_id=user_id, 
                hike_id=rec_data['hike_id']
            ).first()
            
            if not existing:
                rec = Recommendation(
                    user_id=user_id,
                    hike_id=rec_data['hike_id'],
                    confidence_score=rec_data['confidence_score'],
                    recommendation_reason=rec_data['reason']
                )
                db.session.add(rec)
        
        db.session.commit()
        
        # Return recommendations with hike details
        saved_recommendations = Recommendation.query.filter_by(user_id=user_id).order_by(
            Recommendation.confidence_score.desc()
        ).limit(5).all()
        
        return jsonify([rec.to_dict() for rec in saved_recommendations])
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations/<int:rec_id>/viewed', methods=['POST'])
def mark_recommendation_viewed(rec_id):
    """Mark a recommendation as viewed"""
    recommendation = Recommendation.query.get_or_404(rec_id)
    recommendation.is_viewed = True
    db.session.commit()
    
    return jsonify({'message': 'Recommendation marked as viewed'})

@app.route('/api/recommendations/<int:rec_id>/accepted', methods=['POST'])
def mark_recommendation_accepted(rec_id):
    """Mark a recommendation as accepted"""
    recommendation = Recommendation.query.get_or_404(rec_id)
    recommendation.is_accepted = True
    db.session.commit()
    
    return jsonify({'message': 'Recommendation marked as accepted'})

@app.route('/api/stats/<user_id>', methods=['GET'])
def get_user_stats(user_id):
    """Get user hiking statistics"""
    completions = UserCompletion.query.filter_by(user_id=user_id).all()
    
    if not completions:
        return jsonify({
            'total_hikes': 0,
            'total_distance': 0,
            'total_elevation': 0,
            'average_rating': 0,
            'difficulty_distribution': {}
        })
    
    total_distance = sum(float(c.hike.distance_miles) for c in completions)
    total_elevation = sum(c.hike.elevation_gain_feet for c in completions)
    ratings = [c.personal_rating for c in completions if c.personal_rating]
    average_rating = sum(ratings) / len(ratings) if ratings else 0
    
    difficulty_counts = {}
    for completion in completions:
        diff = completion.hike.difficulty_level
        difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
    
    return jsonify({
        'total_hikes': len(completions),
        'total_distance': total_distance,
        'total_elevation': total_elevation,
        'average_rating': round(average_rating, 1),
        'difficulty_distribution': difficulty_counts,
        'recent_hikes': [c.to_dict() for c in completions[-5:]]
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

if __name__ == '__main__':
    with app.app_context():
        init_db()
    
    app.run(debug=True, host='0.0.0.0', port=5001)
