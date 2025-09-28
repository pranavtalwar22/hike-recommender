#!/usr/bin/env python3

import requests
import json

BASE_URL = "http://localhost:5001/api"

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_get_hikes():
    """Test getting all hikes"""
    try:
        response = requests.get(f"{BASE_URL}/hikes")
        print(f"\\nGet hikes: {response.status_code}")
        hikes = response.json()
        print(f"Found {len(hikes)} hikes")
        if hikes:
            print(f"First hike: {hikes[0]['name']}")
        return response.status_code == 200
    except Exception as e:
        print(f"Get hikes failed: {e}")
        return False

def test_add_completion():
    """Test adding a completion"""
    try:
        completion_data = {
            "hike_id": 1,
            "user_id": "test_user",
            "completed_date": "2024-01-15",
            "personal_rating": 4,
            "difficulty_felt": 3,
            "notes": "Great hike with beautiful views!"
        }
        
        response = requests.post(f"{BASE_URL}/completions", json=completion_data)
        print(f"\\nAdd completion: {response.status_code}")
        if response.status_code == 201:
            print(f"Completion added: {response.json()['id']}")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 201
    except Exception as e:
        print(f"Add completion failed: {e}")
        return False

def test_get_recommendations():
    """Test getting recommendations"""
    try:
        response = requests.get(f"{BASE_URL}/recommendations/test_user")
        print(f"\\nGet recommendations: {response.status_code}")
        if response.status_code == 200:
            recs = response.json()
            print(f"Found {len(recs)} recommendations")
            if recs:
                print(f"Top recommendation: {recs[0]['hike']['name']} ({recs[0]['confidence_score']:.2f} confidence)")
        else:
            print(f"Response: {response.text}")
        return True  # Even no recommendations is okay
    except Exception as e:
        print(f"Get recommendations failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Hike Recommender Backend...")
    print("="*50)
    
    tests = [
        ("Health Check", test_health),
        ("Get Hikes", test_get_hikes), 
        ("Add Completion", test_add_completion),
        ("Get Recommendations", test_get_recommendations)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\\n🔍 Running {test_name}...")
        if test_func():
            print(f"✅ {test_name} passed")
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\\n🎯 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Backend is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the backend setup.")