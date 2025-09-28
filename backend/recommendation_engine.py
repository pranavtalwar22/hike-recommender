import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from models import Hike, UserCompletion
import statistics

class RecommendationEngine:
    def __init__(self):
        self.scaler = StandardScaler()
    
    def _extract_user_features(self, completions):
        """Extract user preference features from completed hikes"""
        if not completions:
            return None
        
        # Basic statistics from completed hikes
        distances = [float(c.hike.distance_miles) for c in completions]
        elevations = [c.hike.elevation_gain_feet for c in completions]
        difficulties = [c.hike.difficulty_level for c in completions]
        ratings = [c.personal_rating for c in completions if c.personal_rating]
        difficulty_felt = [c.difficulty_felt for c in completions if c.difficulty_felt]
        
        features = {
            'avg_distance': statistics.mean(distances),
            'max_distance': max(distances),
            'min_distance': min(distances),
            'avg_elevation': statistics.mean(elevations),
            'max_elevation': max(elevations),
            'avg_difficulty': statistics.mean(difficulties),
            'max_difficulty': max(difficulties),
            'total_hikes': len(completions),
            'avg_rating': statistics.mean(ratings) if ratings else 3.0,
            'rating_vs_difficulty_diff': 0  # Will calculate below
        }
        
        # Calculate how user's felt difficulty compares to objective difficulty
        if difficulty_felt and len(difficulty_felt) == len(difficulties):
            diff_comparison = [felt - obj for felt, obj in zip(difficulty_felt, difficulties)]
            features['rating_vs_difficulty_diff'] = statistics.mean(diff_comparison)
        
        return features
    
    def _calculate_hike_features(self, hike):
        """Convert hike attributes to feature vector"""
        return {
            'distance_miles': float(hike.distance_miles),
            'elevation_gain_feet': hike.elevation_gain_feet,
            'difficulty_level': hike.difficulty_level,
            'trail_type_loop': 1 if hike.trail_type == 'loop' else 0,
            'trail_type_out_and_back': 1 if hike.trail_type == 'out-and-back' else 0,
            'trail_type_point_to_point': 1 if hike.trail_type == 'point-to-point' else 0,
        }
    
    def _calculate_difficulty_progression(self, user_features):
        """Suggest appropriate difficulty progression for user"""
        current_max = user_features['max_difficulty']
        current_avg = user_features['avg_difficulty']
        total_hikes = user_features['total_hikes']
        
        # Conservative progression based on experience
        if total_hikes < 3:
            # New hiker - stay within current range or go up by 1
            target_max_difficulty = min(5, current_max + 1)
        elif total_hikes < 10:
            # Intermediate - can handle up to 1 level higher
            target_max_difficulty = min(5, current_max + 1)
        else:
            # Experienced - can handle up to 2 levels higher
            target_max_difficulty = min(5, current_max + 2)
        
        return target_max_difficulty
    
    def _score_hike_for_user(self, hike, user_features, completed_hike_ids):
        """Score how well a hike matches user preferences"""
        # Don't recommend already completed hikes
        if hike.id in completed_hike_ids:
            return 0, "Already completed"
        
        score = 0.0
        reasons = []
        
        # Distance preference scoring
        user_avg_distance = user_features['avg_distance']
        user_max_distance = user_features['max_distance']
        hike_distance = float(hike.distance_miles)
        
        # Prefer hikes within user's range, with slight preference for progression
        if user_avg_distance * 0.5 <= hike_distance <= user_max_distance * 1.3:
            distance_score = 0.3
            if hike_distance > user_avg_distance:
                reasons.append(f"Good progression from your average {user_avg_distance:.1f} miles")
            else:
                reasons.append(f"Comfortable distance similar to your experience")
        elif hike_distance > user_max_distance * 1.3:
            distance_score = 0.1  # Too long
            reasons.append("Longer than your usual hikes - challenging stretch")
        else:
            distance_score = 0.2  # Short hike
            reasons.append("Shorter hike - good for recovery or quick adventure")
        
        score += distance_score
        
        # Elevation preference scoring
        user_avg_elevation = user_features['avg_elevation']
        user_max_elevation = user_features['max_elevation']
        hike_elevation = hike.elevation_gain_feet
        
        if user_avg_elevation * 0.5 <= hike_elevation <= user_max_elevation * 1.2:
            elevation_score = 0.25
            reasons.append("Elevation matches your experience level")
        elif hike_elevation > user_max_elevation * 1.2:
            elevation_score = 0.1
            reasons.append("More elevation gain than usual - good challenge")
        else:
            elevation_score = 0.15
            reasons.append("Moderate elevation - nice recovery hike")
        
        score += elevation_score
        
        # Difficulty progression scoring
        target_max_difficulty = self._calculate_difficulty_progression(user_features)
        hike_difficulty = hike.difficulty_level
        
        if hike_difficulty <= target_max_difficulty:
            if hike_difficulty == user_features['max_difficulty'] + 1:
                difficulty_score = 0.3  # Perfect progression
                reasons.append("Next level challenge - perfect progression")
            elif hike_difficulty == user_features['max_difficulty']:
                difficulty_score = 0.25  # Same level
                reasons.append("Similar difficulty to your recent hikes")
            else:
                difficulty_score = 0.2  # Easier
                reasons.append("More accessible difficulty level")
        else:
            difficulty_score = 0.05  # Too difficult
            reasons.append("Advanced difficulty - save for when you're more experienced")
        
        score += difficulty_score
        
        # Trail type variety bonus
        trail_type_score = 0.1  # Small bonus for variety
        reasons.append(f"Nice {hike.trail_type} trail")
        score += trail_type_score
        
        # User satisfaction prediction
        if user_features['avg_rating'] >= 4.0:
            satisfaction_bonus = 0.05  # User likes challenging hikes
            reasons.append("Matches preferences of hikers who rate highly")
            score += satisfaction_bonus
        
        return min(score, 1.0), " | ".join(reasons)
    
    def generate_recommendations(self, user_id, user_completions, num_recommendations=5):
        """Generate personalized hike recommendations for a user"""
        if not user_completions:
            return []
        
        # Extract user features
        user_features = self._extract_user_features(user_completions)
        completed_hike_ids = {c.hike_id for c in user_completions}
        
        # Get all available hikes
        all_hikes = Hike.query.all()
        
        # Score each hike
        scored_hikes = []
        for hike in all_hikes:
            score, reason = self._score_hike_for_user(hike, user_features, completed_hike_ids)
            if score > 0.1:  # Only include hikes with reasonable scores
                scored_hikes.append({
                    'hike_id': hike.id,
                    'hike': hike,
                    'confidence_score': score,
                    'reason': reason
                })
        
        # Sort by score and return top recommendations
        scored_hikes.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        recommendations = []
        for item in scored_hikes[:num_recommendations]:
            recommendations.append({
                'hike_id': item['hike_id'],
                'confidence_score': item['confidence_score'],
                'reason': item['reason']
            })
        
        return recommendations
    
    def get_user_progression_insights(self, user_completions):
        """Analyze user's hiking progression over time"""
        if len(user_completions) < 2:
            return {"message": "Complete more hikes to see progression insights"}
        
        # Sort by completion date
        sorted_completions = sorted(user_completions, key=lambda x: x.completed_date)
        
        # Analyze progression
        distances = [float(c.hike.distance_miles) for c in sorted_completions]
        elevations = [c.hike.elevation_gain_feet for c in sorted_completions]
        difficulties = [c.hike.difficulty_level for c in sorted_completions]
        
        insights = {
            "distance_trend": "increasing" if distances[-1] > distances[0] else "stable",
            "elevation_trend": "increasing" if elevations[-1] > elevations[0] else "stable",
            "difficulty_trend": "increasing" if difficulties[-1] > difficulties[0] else "stable",
            "total_progression": len([i for i in range(1, len(difficulties)) if difficulties[i] > difficulties[i-1]]),
            "recommended_next_difficulty": min(5, max(difficulties) + 1),
            "ready_for_challenge": max(difficulties) >= 3 and len(user_completions) >= 5
        }
        
        return insights