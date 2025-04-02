#!/bin/bash
# ZephyrPay Auth Test Coverage Runner
# This script runs the auth endpoint tests with proper coverage measurement
# following the ZephyrPay Coding Standards v1.1 requirement of 95%+ coverage for security components

set -e

# Navigate to the root directory
cd "$(dirname "$0")/.."

# Set environment variables for testing
export DATABASE_URL="sqlite:///./test.db"
export SECRET_KEY="testingsecretkey"
export ACCESS_TOKEN_EXPIRE_MINUTES="11520"
export TESTING="True"

# Ensure we have a clean database for testing
mkdir -p backend/app/tests/data
touch backend/app/tests/data/test.db

# Set the Python path to ensure modules are properly found
export PYTHONPATH=$PWD

echo "=== Running pre-import step to ensure modules are tracked ==="
cd backend
python -c "from app.api.v1.endpoints import auth; print(f'Auth module loaded: {auth.__file__}')"

echo "=== Running auth endpoint tests with coverage ==="
python -m coverage run --source=app.api.v1.endpoints.auth -m pytest app/tests/api/v1/test_auth*.py -v

echo "=== Generating coverage report ==="
python -m coverage report -m
python -m coverage xml

# Check the coverage report
if [ -f "coverage.xml" ]; then
  echo "=== Generating coverage badge ==="
  python ../tools/generate_coverage_badge.py coverage.xml
else
  echo "ERROR: No coverage report generated"
  exit 1
fi
