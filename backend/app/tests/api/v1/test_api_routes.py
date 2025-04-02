import pytest
from fastapi.testclient import TestClient

def test_list_all_api_routes(client: TestClient):
    """Test that lists all available API routes for debugging"""
    print("\n==== AVAILABLE API ROUTES ====")
    routes = []
    for route in client.app.routes:
        routes.append(f"Route: {route.path}, methods: {route.methods}")
    
    # Sort routes for better readability
    routes.sort()
    for route in routes:
        print(route)
    
    # Specifically check for roles routes
    roles_routes = [r for r in routes if "/roles/" in r]
    print("\n==== ROLES ROUTES ====")
    for route in roles_routes:
        print(route)
    
    assert True  # This test is just for debugging route registration
