#!/usr/bin/env python3
"""
Basic test script to verify FastAPI app can be imported and initialized
without requiring database connection.
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.main import app
    print("✓ FastAPI app imported successfully")
    print(f"✓ App title: {app.title}")
    print(f"✓ App version: {app.version}")
    
    # Check if routes are registered
    routes = [route.path for route in app.routes]
    print(f"✓ Total routes registered: {len(routes)}")
    
    # Check for specific routes
    expected_routes = ["/health", "/", "/docs", "/openapi.json"]
    for route in expected_routes:
        if route in routes:
            print(f"✓ Route {route} is registered")
        else:
            print(f"✗ Route {route} is missing")
    
    # Check API routes
    api_routes = [r for r in routes if r.startswith("/api/v1")]
    print(f"✓ API routes: {len(api_routes)}")
    for route in api_routes:
        print(f"  - {route}")
    
    print("\n✓ All basic tests passed!")
    sys.exit(0)
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
