#!/bin/bash
# Run Auth Coverage Tests
# 
# This script runs the auth endpoint tests with coverage measurement
# to ensure 95% coverage as per ZephyrPay's Coding Standards V1.1
#

set -e

# Set test environment variables
export DATABASE_URL="sqlite:///./test.db"
export ACCESS_TOKEN_EXPIRE_MINUTES="11520"
export SECRET_KEY="testingsecretkey"
export TESTING="True"
export PYTHONPATH="/Users/tobymorning/ZephyrPay"

# Check if backend directory exists
if [ ! -d "/Users/tobymorning/ZephyrPay/backend" ]; then
  echo "❌ Backend directory not found!"
  exit 1
fi

# Create test data directory if it doesn't exist
mkdir -p /Users/tobymorning/ZephyrPay/backend/app/tests/data
touch /Users/tobymorning/ZephyrPay/backend/app/tests/data/test.db

# Change to backend directory
cd /Users/tobymorning/ZephyrPay/backend

# Set up coverage configuration
echo "[run]" > .coveragerc
echo "source = app.api.v1.endpoints.auth" >> .coveragerc
echo "omit = */tests/*" >> .coveragerc

# Make sure auth module is pre-imported for proper coverage measurement
python -c "import sys; sys.path.insert(0, '.'); from app.api.v1.endpoints import auth; print(f'Auth module available at {auth.__file__}')"

# Check for coverage test file
TEST_FILE=$(find app -name "test_auth_complete_coverage.py")
if [ -z "$TEST_FILE" ]; then
  echo "⚠️ No auth coverage test file found, creating one..."
  python ../.github/scripts/create_auth_coverage_test.py app/tests/api/v1
  TEST_FILE="app/tests/api/v1/test_auth_complete_coverage.py"
fi

# Run tests with coverage measurement
echo "Running auth tests with coverage measurement..."
python -m pytest $TEST_FILE -v \
  --cov=app.api.v1.endpoints.auth \
  --cov-report=xml \
  --cov-report=term \
  --cov-fail-under=95

# Check test result
if [ $? -eq 0 ]; then
  echo "✅ Success! Auth endpoints meet 95% coverage requirement"
else
  echo "❌ Failed to meet 95% coverage requirement for auth endpoints"
  exit 1
fi

# Generate report on YAML file format
echo "Checking YAML syntax of workflow file..."
python -c "
import yaml
import sys
try:
    with open('../.github/workflows/auth-coverage.yml', 'r') as f:
        yaml_content = yaml.safe_load(f)
        print('✅ Workflow YAML syntax is valid')
        # Check that keys are all correct
        expected_keys = ['name', 'on', 'jobs']
        for key in expected_keys:
            if key not in yaml_content:
                print(f'❌ Missing required key: {key}')
                sys.exit(1)
        print('✅ All required keys are present')
        # Check that job has required keys
        for job_name, job in yaml_content.get('jobs', {}).items():
            if 'runs-on' not in job:
                print(f'❌ Job {job_name} is missing required key: runs-on')
                sys.exit(1)
            if 'steps' not in job:
                print(f'❌ Job {job_name} is missing required key: steps')
                sys.exit(1)
        print('✅ Job structure is valid')
except Exception as e:
    print(f'❌ Error validating workflow file: {str(e)}')
    sys.exit(1)
"

echo "✅ Local verification complete"
