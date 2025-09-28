from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import CheckConstraint

db = SQLAlchemy()

class Hike(db.Model):
    __tablename__ = 'hikes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    distance_miles = db.Column(db.Numeric(5, 2), nullable=False)
    elevation_gain_feet = db.Column(db.Integer, nullable=False)
    estimated_duration_hours = db.Column(db.Numeric(3, 1))
    difficulty_level = db.Column(db.Integer, nullable=False)
    trail_type = db.Column(db.String(50))  # 'loop', 'out-and-back', 'point-to-point'
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    completions = db.relationship('UserCompletion', backref='hike', lazy=True)
    recommendations = db.relationship('Recommendation', backref='hike', lazy=True)
    
    __table_args__ = (
        CheckConstraint('difficulty_level >= 1 AND difficulty_level <= 5'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'distance_miles': float(self.distance_miles),
            'elevation_gain_feet': self.elevation_gain_feet,
            'estimated_duration_hours': float(self.estimated_duration_hours) if self.estimated_duration_hours else None,
            'difficulty_level': self.difficulty_level,
            'trail_type': self.trail_type,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserCompletion(db.Model):
    __tablename__ = 'user_completions'
    
    id = db.Column(db.Integer, primary_key=True)
    hike_id = db.Column(db.Integer, db.ForeignKey('hikes.id'), nullable=False)
    user_id = db.Column(db.String(100), nullable=False)
    completed_date = db.Column(db.Date, nullable=False)
    personal_rating = db.Column(db.Integer)
    actual_duration_hours = db.Column(db.Numeric(3, 1))
    weather_conditions = db.Column(db.String(100))
    notes = db.Column(db.Text)
    difficulty_felt = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('personal_rating >= 1 AND personal_rating <= 5'),
        CheckConstraint('difficulty_felt >= 1 AND difficulty_felt <= 5'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'hike_id': self.hike_id,
            'user_id': self.user_id,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'personal_rating': self.personal_rating,
            'actual_duration_hours': float(self.actual_duration_hours) if self.actual_duration_hours else None,
            'weather_conditions': self.weather_conditions,
            'notes': self.notes,
            'difficulty_felt': self.difficulty_felt,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'hike': self.hike.to_dict() if self.hike else None
        }

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    hike_id = db.Column(db.Integer, db.ForeignKey('hikes.id'), nullable=False)
    confidence_score = db.Column(db.Numeric(3, 2), nullable=False)
    recommendation_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_viewed = db.Column(db.Boolean, default=False)
    is_accepted = db.Column(db.Boolean, default=False)
    
    __table_args__ = (
        CheckConstraint('confidence_score >= 0 AND confidence_score <= 1'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'hike_id': self.hike_id,
            'confidence_score': float(self.confidence_score),
            'recommendation_reason': self.recommendation_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_viewed': self.is_viewed,
            'is_accepted': self.is_accepted,
            'hike': self.hike.to_dict() if self.hike else None
        }

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    
    user_id = db.Column(db.String(100), primary_key=True)
    preferred_distance_min = db.Column(db.Numeric(5, 2))
    preferred_distance_max = db.Column(db.Numeric(5, 2))
    preferred_elevation_min = db.Column(db.Integer)
    preferred_elevation_max = db.Column(db.Integer)
    preferred_regions = db.Column(db.Text)  # JSON array
    avoid_regions = db.Column(db.Text)  # JSON array
    fitness_level = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('fitness_level >= 1 AND fitness_level <= 5'),
    )
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'preferred_distance_min': float(self.preferred_distance_min) if self.preferred_distance_min else None,
            'preferred_distance_max': float(self.preferred_distance_max) if self.preferred_distance_max else None,
            'preferred_elevation_min': self.preferred_elevation_min,
            'preferred_elevation_max': self.preferred_elevation_max,
            'preferred_regions': self.preferred_regions,
            'avoid_regions': self.avoid_regions,
            'fitness_level': self.fitness_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }