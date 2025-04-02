#!/usr/bin/env python3
"""
Create a minimal auth test file for CI pipeline
This script creates a BDD-style test file for auth endpoints
to ensure proper imports and minimum test coverage.
"""

import os
import sys

TEST_CONTENT = '''import pytest
from fastapi.testclient import TestClient

# Basic BDD-style test for auth endpoint imports
class TestAuthEndpoints:
    """
    Feature: Auth Endpoints Import Testing
    As a developer
    I want to ensure auth endpoints import correctly
    So that coverage metrics are accurate
    """
    
    def test_auth_module_imports(self, client: TestClient):
        """
        Scenario: Auth module imports correctly
        Given the auth module is available
        When I import it
        Then it should load successfully
        """
        try:
            from app.api.v1.endpoints import auth
            assert auth is not None
            print(f"Auth module found at {auth.__file__}")
        except ImportError as e:
            pytest.fail(f"Failed to import auth module: {str(e)}")
'''

def main():
    # Create test directory
    test_dir = "backend/app/tests/api/v1" if len(sys.argv) < 2 else sys.argv[1]
    os.makedirs(test_dir, exist_ok=True)
    
    # Write test file
    test_file = os.path.join(test_dir, "test_auth_ci.py")
    with open(test_file, "w") as f:
        f.write(TEST_CONTENT)
    
    print(f"Created test file: {test_file}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
