#!/usr/bin/env python
"""
Coverage Runner for Auth Endpoints

This script runs coverage analysis on the authentication endpoints
to ensure that we meet ZephyrPay's 95% coverage requirement.

Important:
- Security-critical components require 95% coverage
- PRs will not be approved without meeting this threshold
"""

import os
import sys
import subprocess
import coverage
import pytest
import importlib.util
import importlib
from pathlib import Path

# Set up proper paths for Python imports
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(BACKEND_DIR))

def run_coverage_analysis():
    """Run coverage analysis on auth endpoints"""
    # Set up environment for testing
    os.environ["TESTING"] = "True"
    os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
    os.environ.setdefault("SECRET_KEY", "testingsecretkey")
    os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "11520")
    
    # Remove any environment variables that might cause validation errors
    if "GITHUB_TOKEN" in os.environ:
        del os.environ["GITHUB_TOKEN"]
    
    # Ensure we can find the auth module
    auth_module_path = BACKEND_DIR / "app" / "api" / "v1" / "endpoints" / "auth.py"
    if not auth_module_path.exists():
        print(f"❌ Auth module not found at {auth_module_path}")
        return False
    
    print(f"✅ Auth module found at {auth_module_path}")
    
    # Now import the auth module
    try:
        # Dynamically import the auth module using importlib
        spec = importlib.util.spec_from_file_location("auth", str(auth_module_path))
        auth_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(auth_module)
        
        # Print auth module details for debugging
        print("Auth routes found:")
        for route in auth_module.router.routes:
            print(f" - {route.path} ({route.methods})")
            print(f"   Endpoint: {route.endpoint.__name__}")
    except Exception as e:
        print(f"❌ Error importing auth module: {str(e)}")
        # Continue anyway as coverage will track imports during test execution
    
    # Create and configure the coverage object
    cov = coverage.Coverage(
        source=['backend.app.api.v1.endpoints.auth'],
        branch=True,
        data_file='.coverage',
        config_file=False,  # Disable searching for config file
        omit=['**/__pycache__/*', '**/.venv/*', '**/tests/*']
    )
    
    try:
        # Start coverage measurement
        cov.start()
        
        # Run pytest specifically on auth tests
        test_file = BACKEND_DIR / "app" / "tests" / "api" / "v1" / "test_auth_complete_coverage.py"
        result = pytest.main([
            str(test_file),
            "-v",
            "--no-header",
            "--no-summary",
        ])
    finally:
        # Stop coverage measurement
        cov.stop()
        cov.save()
    
    try:
        # Generate reports
        print("\nCoverage Report:")
        total_coverage = cov.report(show_missing=True)
        cov.xml_report(outfile='auth_coverage.xml')
        cov.html_report(directory='auth_coverage_html')
        
        # Check if we meet the 95% threshold
        if total_coverage >= 95.0:
            print(f"✅ Auth endpoint coverage: {total_coverage:.2f}% (meets 95% requirement)")
            return True
        else:
            print(f"❌ Auth endpoint coverage: {total_coverage:.2f}% (below 95% requirement)")
            return False
    except Exception as e:
        print(f"❌ Error generating coverage report: {str(e)}")
        return False

if __name__ == "__main__":
    print("Running coverage analysis for auth endpoints...")
    success = run_coverage_analysis()
    sys.exit(0 if success else 1)
