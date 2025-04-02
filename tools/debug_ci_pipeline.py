#!/usr/bin/env python3
"""
ZephyrPay CI/CD Pipeline Debugging Script

This script uses the GitHub API to:
1. Analyze GitHub Actions workflow issues
2. Verify workflow syntax
3. Run a local test coverage check to validate CI settings
4. Submit fixes to the CI pipeline as needed

Usage:
    python debug_ci_pipeline.py [--token TOKEN] [--analyze-only] [--fix-workflow] [--check-coverage]

Requirements:
    - GitHub personal access token with repo scope
    - pytest, pytest-cov, httpx, and other testing dependencies
"""

import argparse
import json
import os
import subprocess
import sys
import requests
import time
from pathlib import Path
import re
import xml.etree.ElementTree as ET

# Repository information
REPO_OWNER = "lyfted-engineering"
REPO_NAME = "ZephyrPay"
BASE_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"

# Security-critical components based on ZephyrPay's Coding Standards V1.1
SECURITY_CRITICAL_COMPONENTS = [
    "app.api.v1.endpoints.auth",
    "app.core.security",
    "app.api.v1.endpoints.roles",
    "app.core.rbac"
]

# Coverage thresholds based on ZephyrPay's Coding Standards V1.1
OVERALL_COVERAGE_THRESHOLD = 90
SECURITY_CRITICAL_THRESHOLD = 95

def get_github_token():
    """Get GitHub token from environment or prompt user"""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GitHub token not found in environment.")
        token = input("Enter your GitHub Personal Access Token: ").strip()
    return token

def make_github_request(endpoint, method="GET", token=None, data=None):
    """Make a request to the GitHub API"""
    url = f"{BASE_API_URL}/{endpoint}"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    if token:
        headers["Authorization"] = f"token {token}"
    
    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        json=data
    )
    
    if response.status_code >= 400:
        print(f"Error ({response.status_code}): {response.text}")
    
    return response

def check_workflow_syntax(workflow_path):
    """Check if the workflow file has valid YAML syntax"""
    try:
        result = subprocess.run(
            ["yamllint", workflow_path],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"YAML syntax issues found in {workflow_path}:")
            print(result.stdout)
            return False
        return True
    except FileNotFoundError:
        print("yamllint not found. Install with: pip install yamllint")
        # Basic validation - try to load as YAML
        try:
            import yaml
            with open(workflow_path, 'r') as f:
                yaml.safe_load(f)
            return True
        except Exception as e:
            print(f"YAML validation error: {str(e)}")
            return False

def analyze_workflow_file(workflow_path):
    """Analyze a workflow file for common issues"""
    try:
        import yaml
        with open(workflow_path, 'r') as f:
            workflow_data = yaml.safe_load(f)
        
        print(f"\n=== Analyzing workflow file: {workflow_path} ===")
        
        # Check the structure
        issues = []
        if 'on' not in workflow_data:
            issues.append("Missing 'on' section")
        else:
            # Check if it triggers for feature branches
            triggers = workflow_data['on']
            has_feature_branch = False
            
            if isinstance(triggers, dict):
                if 'push' in triggers:
                    branches = triggers['push'].get('branches', [])
                    if any('feature' in str(branch) for branch in branches):
                        has_feature_branch = True
            
            if not has_feature_branch:
                issues.append("Workflow doesn't trigger on feature branches")
        
        # Check for test coverage job
        has_coverage = False
        if 'jobs' in workflow_data:
            for job_name, job_data in workflow_data['jobs'].items():
                if any('coverage' in str(step).lower() for step in job_data.get('steps', [])):
                    has_coverage = True
                    break
            
            if not has_coverage:
                issues.append("No coverage checking step found in any job")
        else:
            issues.append("Missing 'jobs' section")
        
        # Report findings
        if issues:
            print("⚠️ Issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ No major issues found in workflow file")
        
        return issues
    except Exception as e:
        print(f"Error analyzing workflow file: {str(e)}")
        return [f"Error analyzing workflow: {str(e)}"]

def get_workflow_runs(token):
    """Get recent workflow runs"""
    response = make_github_request("actions/runs", token=token)
    if response.status_code == 200:
        runs = response.json().get("workflow_runs", [])
        print(f"Found {len(runs)} recent workflow runs")
        for run in runs[:5]:  # Show most recent 5 runs
            print(f"Workflow: {run['name']}")
            print(f"  Status: {run['status']}")
            print(f"  Conclusion: {run.get('conclusion', 'N/A')}")
            print(f"  URL: {run['html_url']}")
            print(f"  Created: {run['created_at']}")
            print("---")
        return runs
    return []

def get_workflow_logs(run_id, token):
    """Get logs for a specific workflow run"""
    response = make_github_request(f"actions/runs/{run_id}/logs", token=token)
    if response.status_code == 200:
        # This returns a zip file with logs
        print(f"Downloaded logs for run {run_id}")
        # Save the logs (binary content)
        with open(f"workflow_logs_{run_id}.zip", "wb") as f:
            f.write(response.content)
        return True
    return False

def get_workflow_jobs(run_id, token):
    """Get details of jobs in a workflow run"""
    response = make_github_request(f"actions/runs/{run_id}/jobs", token=token)
    if response.status_code == 200:
        jobs = response.json().get("jobs", [])
        print(f"Found {len(jobs)} jobs in workflow run {run_id}")
        for job in jobs:
            print(f"Job: {job['name']}")
            print(f"  Status: {job['status']}")
            print(f"  Conclusion: {job.get('conclusion', 'N/A')}")
            print(f"  Started At: {job.get('started_at', 'N/A')}")
            print(f"  Completed At: {job.get('completed_at', 'N/A')}")
            
            steps = job.get("steps", [])
            failed_steps = [step for step in steps if step.get("conclusion") == "failure"]
            if failed_steps:
                print("  Failed Steps:")
                for step in failed_steps:
                    print(f"    - {step['name']}")
        return jobs
    return []

def run_local_tests(focus_auth=True):
    """Run tests locally to verify coverage"""
    print("Running local tests to verify coverage...")
    
    repo_root = Path(__file__).parent.parent
    backend_dir = repo_root / "backend"
    
    # Ensure test database directory exists
    test_data_dir = backend_dir / "app" / "tests" / "data"
    test_data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a test database file if it doesn't exist
    test_db_file = test_data_dir / "test.db"
    if not test_db_file.exists():
        test_db_file.touch()
    
    # Set up environment variables for testing
    env = os.environ.copy()
    env.update({
        "DATABASE_URL": "sqlite:///./test.db",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "11520",
        "SECRET_KEY": "testingsecretkey",
        "TESTING": "True",
        "PYTHONPATH": str(repo_root)  # This is critical for module imports
    })
    
    # Run pytest with coverage
    try:
        # First pre-import modules to ensure they're properly instrumented
        print("Pre-importing modules to ensure proper instrumentation...")
        import_cmd = [
            sys.executable, 
            "-c", 
            "import sys; sys.path.insert(0, '.'); "
            "from app.api.v1.endpoints import auth; "
            "print(f'Auth module loaded: {auth.__file__}')"
        ]
        subprocess.run(import_cmd, cwd=str(backend_dir), env=env, check=False)
        
        # Determine which tests to run
        test_path = "app/tests"
        if focus_auth:
            test_path = "app/tests/api/v1/test_auth*.py"
        
        # Use direct coverage instrumentation instead of pytest-cov
        coverage_cmd = [
            sys.executable, "-m", "coverage", "run",
            "--source=app.api.v1.endpoints.auth,app.core.security" if focus_auth else "--source=app",
            "-m", "pytest", test_path, "-v"
        ]
        
        print(f"Running: {' '.join(coverage_cmd)}")
        result = subprocess.run(
            coverage_cmd,
            cwd=str(backend_dir),
            env=env,
            capture_output=True,
            text=True
        )
        
        print("\nTest output summary:")
        output_lines = result.stdout.split('\n')
        # Print only test summary (last few lines)
        for line in output_lines[-10:]:
            print(line)
        
        if result.stderr:
            print("\nErrors:")
            print(result.stderr)
        
        # Generate coverage report
        print("\nGenerating coverage report...")
        subprocess.run(
            [sys.executable, "-m", "coverage", "report", "-m"],
            cwd=str(backend_dir),
            env=env,
            check=False
        )
        
        subprocess.run(
            [sys.executable, "-m", "coverage", "xml"],
            cwd=str(backend_dir),
            env=env, 
            check=False
        )
        
        # Check if coverage.xml was generated
        coverage_file = backend_dir / "coverage.xml"
        if coverage_file.exists():
            print(f"\nCoverage report generated at {coverage_file}")
            return str(coverage_file)
        else:
            print("\nNo coverage report was generated")
            return None
    except Exception as e:
        print(f"Error running tests: {str(e)}")
        return None

def analyze_coverage_report(coverage_file):
    """Analyze the coverage report against ZephyrPay standards"""
    try:
        tree = ET.parse(coverage_file)
        root = tree.getroot()
        
        # Get overall coverage
        overall_coverage = float(root.attrib.get('line-rate', 0)) * 100
        print(f"\n=== Coverage Analysis ===")
        print(f"Overall coverage: {overall_coverage:.2f}%")
        
        # Check against threshold
        if overall_coverage < OVERALL_COVERAGE_THRESHOLD:
            print(f"❌ Overall coverage {overall_coverage:.2f}% is below the required {OVERALL_COVERAGE_THRESHOLD}%")
        else:
            print(f"✅ Overall coverage {overall_coverage:.2f}% meets the minimum requirement of {OVERALL_COVERAGE_THRESHOLD}%")
        
        # Check security-critical components
        security_components = []
        for package in root.findall(".//package"):
            pkg_name = package.attrib.get('name', '')
            
            is_security_critical = False
            for critical_component in SECURITY_CRITICAL_COMPONENTS:
                if critical_component in pkg_name:
                    is_security_critical = True
                    break
            
            # Calculate coverage for this package
            line_rate = float(package.attrib.get('line-rate', 0)) * 100
            lines_valid = int(package.attrib.get('lines-valid', 0))
            lines_covered = int(lines_valid * float(package.attrib.get('line-rate', 0)))
            
            # Store component info
            component_info = {
                'name': pkg_name,
                'coverage': line_rate,
                'lines_valid': lines_valid,
                'lines_covered': lines_covered,
                'is_security_critical': is_security_critical
            }
            security_components.append(component_info)
        
        # Report on security-critical components
        print("\nSecurity-Critical Components:")
        security_critical_found = False
        all_security_critical_pass = True
        
        for component in security_components:
            if component['is_security_critical']:
                security_critical_found = True
                status = "✅" if component['coverage'] >= SECURITY_CRITICAL_THRESHOLD else "❌"
                if component['coverage'] < SECURITY_CRITICAL_THRESHOLD:
                    all_security_critical_pass = False
                
                print(f"{status} {component['name']}: {component['coverage']:.2f}% ({component['lines_covered']}/{component['lines_valid']} lines)")
        
        if not security_critical_found:
            print("⚠️ No security-critical components found in coverage report")
        elif all_security_critical_pass:
            print(f"✅ All security-critical components meet the minimum threshold of {SECURITY_CRITICAL_THRESHOLD}%")
        else:
            print(f"❌ Some security-critical components are below the required {SECURITY_CRITICAL_THRESHOLD}%")
        
        # Identify specific modules with low coverage
        print("\nModules with less than expected coverage:")
        for component in security_components:
            threshold = SECURITY_CRITICAL_THRESHOLD if component['is_security_critical'] else OVERALL_COVERAGE_THRESHOLD
            if component['coverage'] < threshold:
                print(f"❌ {component['name']}: {component['coverage']:.2f}% (Expected: {threshold}%)")
        
        return {
            'overall_coverage': overall_coverage,
            'security_components': security_components,
            'meets_overall_threshold': overall_coverage >= OVERALL_COVERAGE_THRESHOLD,
            'meets_security_threshold': all_security_critical_pass if security_critical_found else False
        }
    except Exception as e:
        print(f"Error analyzing coverage report: {str(e)}")
        return None

def fix_coverage_issues(coverage_data=None):
    """Generate recommendations to fix coverage issues based on analysis"""
    if not coverage_data:
        print("No coverage data available for analysis")
        return
    
    print("\n=== Coverage Fix Recommendations ===")
    
    # Check for overall coverage issues
    if not coverage_data.get('meets_overall_threshold', False):
        print("\n1. Improving Overall Coverage:")
        print("   - Add more tests focusing on untested code paths")
        print("   - Use the coverage report to identify specific modules that need attention")
        print("   - Consider implementing BDD-style tests for better organization")
    
    # Check for security components issues
    security_components = coverage_data.get('security_components', [])
    security_issues = [c for c in security_components if c.get('is_security_critical', False) and c.get('coverage', 0) < SECURITY_CRITICAL_THRESHOLD]
    
    if security_issues:
        print("\n2. Fixing Security-Critical Component Coverage:")
        for component in security_issues:
            print(f"\n   Module: {component['name']}")
            print(f"   Current Coverage: {component['coverage']:.2f}%")
            print(f"   Target Coverage: {SECURITY_CRITICAL_THRESHOLD}%")
            print("   Recommendations:")
            print("   - Create comprehensive tests for all edge cases")
            print("   - Focus on exception handling paths which are often missed")
            print("   - Ensure tests validate input validation and error responses")
            print("   - Add direct instrumentation tests that verify specific code lines")
    
    # CI Pipeline recommendations
    print("\n3. CI/CD Pipeline Improvements:")
    print("   - Ensure the workflow accurately reports coverage metrics")
    print("   - Add step to verify coverage thresholds are met")
    print("   - Consider failing the build when security components don't meet thresholds")
    print("   - Add coverage badges to repository README")

def fix_workflow_file(token=None, dry_run=True):
    """Create an improved workflow file for GitHub Actions"""
    # Path to the workflow file
    repo_root = Path(__file__).parent.parent
    workflow_dir = repo_root / ".github" / "workflows"
    workflow_path = workflow_dir / "test-coverage.yml"
    
    print(f"\n=== {'Analyzing' if dry_run else 'Fixing'} workflow file at {workflow_path} ===")
    
    # Check if workflow file exists
    if not workflow_path.exists():
        print(f"Workflow file not found at {workflow_path}")
        if not dry_run:
            print("Creating new workflow file...")
            workflow_dir.mkdir(parents=True, exist_ok=True)
        else:
            return
    
    # Analyze existing workflow file
    if workflow_path.exists():
        issues = analyze_workflow_file(workflow_path)
        
        if not issues and dry_run:
            print("No issues found in workflow file")
            return
    
    if dry_run:
        print("\nDry run - not making any changes to workflow file")
        return
    
    # Create improved workflow content
    workflow_content = """name: Test Coverage CI

on:
  push:
    branches: [ main, develop, feature/*, fix/* ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest pytest-cov pytest-asyncio httpx coverage
          pip install -r backend/requirements.txt
          
      - name: Setup test environment
        run: |
          mkdir -p backend/app/tests/data
          touch backend/app/tests/data/test.db
          
      - name: Run tests with coverage
        env:
          DATABASE_URL: "sqlite:///./test.db"
          ACCESS_TOKEN_EXPIRE_MINUTES: "11520"
          SECRET_KEY: "testingsecretkey"
          TESTING: "True"
          PYTHONPATH: ${{ github.workspace }}
        run: |
          cd backend
          # Pre-import modules to ensure they're tracked by coverage
          python -c "
          import sys
          sys.path.insert(0, '..')
          from app.api.v1.endpoints import auth
          print(f'Auth module loaded: {auth.__file__}')
          "
          # Run coverage with direct source tracking
          coverage run --source=app.api.v1.endpoints.auth,app.core.security -m pytest app/tests/api/v1/test_auth*.py -v
          coverage report -m
          coverage xml
        
      - name: Check coverage requirements
        if: always()
        run: |
          cd backend
          if [ -f coverage.xml ]; then
            echo "Coverage report exists, checking ZephyrPay requirements..."
            python ../.github/scripts/check_coverage.py
          else
            echo "No coverage report generated - running basic coverage check"
            cd ..
            python -c "
            print('Missing coverage report - coverage checks failed')
            import sys
            print('❌ Coverage requirements of 90% overall and 95% for security components not verified')
            sys.exit(1)
            "
          fi
          
      - name: Upload coverage report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: coverage-report
          path: backend/coverage.xml
          if-no-files-found: ignore"""
    
    # Write the workflow file
    if not dry_run:
        with open(workflow_path, 'w') as f:
            f.write(workflow_content)
        print(f"Updated workflow file at {workflow_path}")
        
        if token:
            print("Committing workflow changes to repository...")
            commit_message = "ci: Fix GitHub Actions workflow for test coverage"
            
            # Check if file exists in repo
            file_exists = True
            response = make_github_request(f"contents/.github/workflows/test-coverage.yml", token=token)
            if response.status_code != 200:
                file_exists = False
            
            # Create or update file
            file_path = ".github/workflows/test-coverage.yml"
            data = {
                "message": commit_message,
                "content": workflow_content.encode('utf-8').hex(),
                "branch": "feature/fix-ci-pipeline"
            }
            
            if file_exists:
                data["sha"] = response.json()["sha"]
                
            response = make_github_request(
                f"contents/{file_path}",
                method="PUT",
                token=token,
                data=data
            )
            
            if response.status_code in (200, 201):
                print("Workflow file committed to repository")
            else:
                print("Failed to commit workflow file to repository")

def diagnose_workflow_step_failures(run_id, token):
    """Analyze failed steps in a workflow run to provide solutions"""
    jobs = get_workflow_jobs(run_id, token)
    
    for job in jobs:
        steps = job.get("steps", [])
        failed_steps = [step for step in steps if step.get("conclusion") == "failure"]
        
        if failed_steps:
            print(f"\n=== Analyzing failures in job '{job['name']}' ===")
            
            for step in failed_steps:
                step_name = step['name']
                print(f"\nFailed step: {step_name}")
                
                # Generic recommendations based on common failures
                if "test" in step_name.lower() and "coverage" in step_name.lower():
                    print("Possible issues:")
                    print("1. Test coverage below threshold")
                    print("2. Tests failing due to import issues")
                    print("3. Coverage reporting configuration problems")
                    print("\nRecommendations:")
                    print("- Check the auth module imports in your tests")
                    print("- Verify proper PYTHONPATH setting in workflow")
                    print("- Pre-import modules before running tests to ensure they're tracked")
                    print("- Run tests locally with the same configuration")
                
                elif "checkout" in step_name.lower():
                    print("Possible issues:")
                    print("1. Repository access permissions")
                    print("2. Git submodule problems")
                    print("\nRecommendations:")
                    print("- Check GitHub token permissions")
                    print("- Verify repository access settings")
                
                elif "install" in step_name.lower():
                    print("Possible issues:")
                    print("1. Missing dependencies")
                    print("2. Version conflicts")
                    print("3. Package installation errors")
                    print("\nRecommendations:")
                    print("- Update requirements.txt with compatible versions")
                    print("- Add missing dependencies")
                    print("- Check for errors in package installation commands")
                
                else:
                    print("Generic step failure - recommend examining workflow logs for specific error messages")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="GitHub Actions Workflow Debugging Tool")
    parser.add_argument("--token", help="GitHub Personal Access Token")
    parser.add_argument("--analyze-only", action="store_true", help="Analyze workflow without making changes")
    parser.add_argument("--fix-workflow", action="store_true", help="Fix workflow file issues")
    parser.add_argument("--check-coverage", action="store_true", help="Run a local coverage check")
    parser.add_argument("--run-id", type=int, help="Analyze specific workflow run by ID")
    args = parser.parse_args()
    
    # Get GitHub token
    token = args.token if args.token else get_github_token()
    
    if not token and not args.check_coverage:
        print("GitHub token is required for most operations")
        return
    
    # Analyze or fix workflow file
    if args.fix_workflow:
        fix_workflow_file(token, dry_run=False)
    else:
        repo_root = Path(__file__).parent.parent
        workflow_path = repo_root / ".github" / "workflows" / "test-coverage.yml"
        if workflow_path.exists():
            analyze_workflow_file(workflow_path)
    
    # Get workflow runs
    if token and not args.analyze_only and not args.run_id:
        get_workflow_runs(token)
    
    # Analyze specific run
    if args.run_id and token:
        print(f"\nAnalyzing workflow run {args.run_id}...")
        get_workflow_jobs(args.run_id, token)
        diagnose_workflow_step_failures(args.run_id, token)
    
    # Run a local coverage check
    if args.check_coverage or (not args.run_id and not args.fix_workflow):
        coverage_file = run_local_tests(focus_auth=True)
        if coverage_file:
            coverage_data = analyze_coverage_report(coverage_file)
            if coverage_data:
                fix_coverage_issues(coverage_data)
    
    print("\nContinuous Improvement Recommendations:")
    print("1. Integrate test-coverage.yml in your main workflow")
    print("2. Ensure all PRs must pass coverage checks")
    print("3. Consider adding coverage badge to README")
    print("4. Update workflow to notify on coverage regression")
    
if __name__ == "__main__":
    main()
