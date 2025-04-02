# ZephyrPay Testing & CI/CD Tools

This directory contains tools for testing, coverage verification, and CI/CD pipeline management that follow ZephyrPay's Coding Standards V1.1.

## Core Tools

### Coverage Verification

- **`verify_coverage_standards.py`**: Comprehensive tool to verify code meets ZephyrPay's coverage standards (90% overall, 95% for security components). Can automatically generate BDD-style test templates for uncovered code.

  ```bash
  # Check all components
  ./verify_coverage_standards.py
  
  # Check only auth endpoints
  ./verify_coverage_standards.py --auth-only
  
  # Generate test templates for missing coverage
  ./verify_coverage_standards.py --fix-issues
  ```

- **`run_auth_tests.sh`**: Focused script for running auth endpoint tests and verifying their coverage meets the 95% threshold required for security-critical components.

### CI/CD Pipeline Management

- **`debug_ci_pipeline.py`**: Comprehensive CI/CD pipeline debugging tool to diagnose build failures, workflow issues, and coverage problems.

  ```bash
  # Debug workflow syntax and execution
  ./debug_ci_pipeline.py --token YOUR_GITHUB_TOKEN
  
  # Check coverage locally
  ./debug_ci_pipeline.py --check-coverage
  
  # Fix workflow file issues
  ./debug_ci_pipeline.py --fix-workflow
  ```

- **`update_workflow.py`**: Utility for generating improved GitHub Actions workflow files.

## BDD Testing Workflow (from ZephyrPay Coding Standards V1.1)

Our tools support the ZephyrPay BDD testing workflow:

1. **Red Stage**: Write failing tests for features and code paths
2. **Green Stage**: Implement functionality to make tests pass
3. **Refactor Stage**: Clean up code while maintaining passing tests

The `verify_coverage_standards.py` tool with `--fix-issues` facilitates this workflow by generating BDD-style test templates for uncovered code paths.

## Security Component Coverage Requirements

ZephyrPay's Coding Standards V1.1 requires:

- 90% minimum coverage for all components
- 95% minimum coverage for security-critical components:
  - Auth endpoints
  - Core security modules
  - Role-based access control
  - Payment processing

Our tools automatically verify compliance with these standards.

## No-Mock Testing Policy

In line with ZephyrPay's No-Mock testing policy, our tools encourage comprehensive integration testing that doesn't rely on mocks or simulated components for security-critical functionality.

## Pre-Commit Workflow

To ensure changes meet ZephyrPay standards before submitting PRs:

1. Make your code changes
2. Run `./verify_coverage_standards.py` to check coverage
3. If coverage is insufficient, use `--fix-issues` to generate test templates
4. Implement missing tests following the BDD patterns
5. Verify coverage again before committing

This workflow ensures all PRs meet ZephyrPay's stringent coverage requirements.
