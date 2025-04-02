#!/usr/bin/env python3
"""
Debug GitHub Actions Workflow

This tool helps diagnose issues with GitHub Actions workflows
according to ZephyrPay's Coding Standards V1.1 requirements.
"""

import sys
import os
import yaml
import json
import subprocess
import argparse
from pathlib import Path

def check_workflow_syntax(workflow_path):
    """Check if a workflow file has valid YAML syntax."""
    try:
        with open(workflow_path, 'r') as f:
            yaml_content = yaml.safe_load(f)
            print(f"✅ Workflow file {workflow_path} has valid YAML syntax")
            return yaml_content
    except yaml.YAMLError as e:
        print(f"❌ Workflow file {workflow_path} has invalid YAML syntax:")
        print(f"   {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Error reading workflow file {workflow_path}: {str(e)}")
        return None

def validate_workflow_structure(workflow_content):
    """Validate the structure of a GitHub Actions workflow."""
    errors = []
    
    # Check for required fields
    if 'name' not in workflow_content:
        errors.append("Missing 'name' field in workflow")
    
    if 'on' not in workflow_content:
        errors.append("Missing 'on' field in workflow (trigger events)")
    
    if 'jobs' not in workflow_content:
        errors.append("Missing 'jobs' field in workflow")
    else:
        # Check if there are any jobs defined
        if not workflow_content['jobs']:
            errors.append("No jobs defined in workflow")
        else:
            # Check each job for required fields
            for job_name, job in workflow_content['jobs'].items():
                if 'runs-on' not in job:
                    errors.append(f"Job '{job_name}' is missing 'runs-on' field")
                if 'steps' not in job:
                    errors.append(f"Job '{job_name}' is missing 'steps' field")
                elif not job['steps']:
                    errors.append(f"Job '{job_name}' has no steps defined")
    
    # Report results
    if errors:
        print("❌ Workflow structure validation failed:")
        for error in errors:
            print(f"   - {error}")
        return False
    else:
        print("✅ Workflow structure validation passed")
        return True

def check_permissions(token, repo_owner, repo_name):
    """Check if the provided GitHub token has necessary permissions."""
    try:
        # Attempt to make a simple API call to check token validity
        cmd = ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
               '-H', f'Authorization: token {token}',
               f'https://api.github.com/repos/{repo_owner}/{repo_name}']
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        status_code = result.stdout.strip()
        
        if status_code == '200':
            print(f"✅ GitHub token has read access to {repo_owner}/{repo_name}")
            return True
        elif status_code == '404':
            print(f"❌ Repository {repo_owner}/{repo_name} not found or token doesn't have access")
            return False
        elif status_code == '401':
            print("❌ GitHub token is invalid or expired")
            return False
        else:
            print(f"❌ Unexpected status code when checking token permissions: {status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Error checking token permissions: {str(e)}")
        return False

def check_secrets(workflow_content):
    """Check for missing secrets referenced in the workflow file."""
    secrets_used = []
    
    def find_secrets(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and '${{' in value and 'secrets.' in value:
                    # Extract secret names from ${{ secrets.SECRET_NAME }}
                    import re
                    matches = re.findall(r'\$\{\{\s*secrets\.([A-Za-z0-9_]+)\s*\}\}', value)
                    secrets_used.extend(matches)
                else:
                    find_secrets(value)
        elif isinstance(obj, list):
            for item in obj:
                find_secrets(item)
    
    find_secrets(workflow_content)
    
    if secrets_used:
        print(f"Found {len(secrets_used)} secrets referenced in workflow:")
        for secret in sorted(set(secrets_used)):
            print(f"   - {secret}")
        print("\nEnsure these secrets are properly set in your repository settings.")
    else:
        print("No secrets referenced in the workflow file.")

def main():
    parser = argparse.ArgumentParser(description='Debug GitHub Actions workflows')
    parser.add_argument('--token', help='GitHub token for API calls')
    parser.add_argument('--repo', help='Repository in format owner/name', default='lyfted-engineering/ZephyrPay')
    parser.add_argument('--workflow', help='Path to workflow file to check')
    parser.add_argument('--all-workflows', action='store_true', help='Check all workflow files')
    
    args = parser.parse_args()
    
    # Split repository into owner and name
    if '/' in args.repo:
        repo_owner, repo_name = args.repo.split('/', 1)
    else:
        print("❌ Repository should be specified as owner/name")
        return 1
    
    # Check token if provided
    if args.token:
        if not check_permissions(args.token, repo_owner, repo_name):
            print("⚠️ Continuing with limited functionality due to token issues")
    else:
        print("⚠️ No GitHub token provided, skipping permission checks")
    
    # Determine which workflow files to check
    workflow_files = []
    if args.all_workflows:
        workflow_dir = Path('.github/workflows')
        if workflow_dir.exists():
            workflow_files = list(workflow_dir.glob('*.yml'))
            workflow_files.extend(list(workflow_dir.glob('*.yaml')))
        else:
            print("❌ .github/workflows directory not found")
            return 1
    elif args.workflow:
        workflow_path = Path(args.workflow)
        if workflow_path.exists():
            workflow_files = [workflow_path]
        else:
            print(f"❌ Workflow file {args.workflow} not found")
            return 1
    else:
        # Default to test-coverage.yml if it exists
        default_workflow = Path('.github/workflows/test-coverage.yml')
        if default_workflow.exists():
            workflow_files = [default_workflow]
            print(f"No workflow specified, defaulting to {default_workflow}")
        else:
            print("❌ No workflow specified and default test-coverage.yml not found")
            print("   Use --workflow or --all-workflows to specify which files to check")
            return 1
    
    # Check each workflow file
    success = True
    for workflow_file in workflow_files:
        print(f"\n{'=' * 50}")
        print(f"Checking workflow: {workflow_file}")
        print(f"{'=' * 50}")
        
        workflow_content = check_workflow_syntax(workflow_file)
        if workflow_content:
            if not validate_workflow_structure(workflow_content):
                success = False
            check_secrets(workflow_content)
        else:
            success = False
    
    # Generate a report
    print(f"\n{'=' * 50}")
    print("GitHub Actions Workflow Debug Report")
    print(f"{'=' * 50}")
    print(f"Repository: {repo_owner}/{repo_name}")
    print(f"Workflows checked: {len(workflow_files)}")
    print(f"Overall status: {'✅ PASSED' if success else '❌ ISSUES FOUND'}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
