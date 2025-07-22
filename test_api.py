#!/usr/bin/env python3
"""
Test script for Team Management API endpoints
"""
import json
import requests

# API base URL
BASE_URL = "http://127.0.0.1:8000/api"

def test_api_endpoints():
    """Test all the API endpoints"""
    print("🧪 Testing Team Management API Endpoints...")
    print("=" * 50)
    
    # Test 1: List all teams (should be empty initially)
    print("\n1. Testing GET /api/teams/ (List all teams)")
    try:
        response = requests.get(f"{BASE_URL}/teams/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Create a new team
    print("\n2. Testing POST /api/teams/ (Create a new team)")
    team_data = {
        "name": "Development Team",
    }
    try:
        response = requests.post(f"{BASE_URL}/teams/", json=team_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 201:
            created_team = response.json()
            team_id = created_team['id']
            print(f"Response: {json.dumps(created_team, indent=2)}")
            print(f"✅ Team created with ID: {team_id}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
        team_id = None
    
    # Test 3: Create another team
    print("\n3. Testing POST /api/teams/ (Create another team)")
    team_data2 = {
        "name": "QA Team",
    }
    try:
        response = requests.post(f"{BASE_URL}/teams/", json=team_data2)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 201:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print("✅ Second team created successfully")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: List all teams again (should show created teams)
    print("\n4. Testing GET /api/teams/ (List all teams after creation)")
    try:
        response = requests.get(f"{BASE_URL}/teams/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Get specific team by ID
    if team_id:
        print(f"\n5. Testing GET /api/teams/{team_id}/ (Get team by ID)")
        try:
            response = requests.get(f"{BASE_URL}/teams/{team_id}/")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Test 6: List all users
    print("\n6. Testing GET /api/users/ (List all users)")
    try:
        response = requests.get(f"{BASE_URL}/users/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API Testing Complete!")
    print("\nAPI Endpoints Available:")
    print("- GET  /api/teams/     - List all teams")
    print("- POST /api/teams/     - Create a new team")
    print("- GET  /api/teams/{id}/ - Get team by ID")
    print("- GET  /api/users/     - List all users")
    print("- POST /api/users/     - Create a new user")
    print("- GET  /api/users/{id}/ - Get user by ID")

if __name__ == "__main__":
    test_api_endpoints()
