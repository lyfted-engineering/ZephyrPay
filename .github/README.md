# ZephyrPay CI/CD Pipeline

This document describes the CI/CD pipeline configuration for ZephyrPay, following the V1.1 coding standards.

## Coverage Requirements

ZephyrPay adheres to strict coverage requirements as defined in our Coding Standards V1.1:

- **Overall Coverage**: Minimum 90% code coverage
- **Security-Critical Components**: Minimum 95% code coverage
  - Auth endpoints
  - Security core modules
  - Role-based access control
  - Payment processing

## Workflow Files

- **Security Coverage CI** (`.github/workflows/test-coverage.yml`): Ensures that security-critical components meet the 95% coverage threshold.

## Coverage Scripts

The following scripts are used to verify coverage compliance:

- `.github/scripts/verify_security_coverage.py`: Verifies that auth endpoints meet the 95% security coverage threshold.
- `tools/debug_ci_pipeline.py`: Comprehensive CI/CD pipeline debugging tool to troubleshoot workflow issues.
- `backend/run_auth_coverage.py`: Local utility to check auth coverage before pushing.

## Running Tests Locally

Before submitting a PR, verify coverage meets standards:

```bash
# Run from repository root
cd /path/to/ZephyrPay

# Set environment variables (if not in .env file)
export DATABASE_URL="sqlite:///./test.db"
export SECRET_KEY="testingsecretkey"
export ACCESS_TOKEN_EXPIRE_MINUTES="11520"
export TESTING="True"

# Run auth tests with coverage check
cd backend
python -m pytest app/tests/api/v1/test_auth*.py -v --cov=app.api.v1.endpoints.auth --cov-report=term
```

## Enforcement Policy

- PRs failing the coverage requirements will not be approved
- All security-critical components must maintain 95% test coverage
- New features must include tests meeting coverage requirements

## Troubleshooting

If the CI pipeline fails, use the debug script:

```bash
python tools/debug_ci_pipeline.py --check-coverage
```

This will diagnose coverage issues and provide specific recommendations for improvement.
