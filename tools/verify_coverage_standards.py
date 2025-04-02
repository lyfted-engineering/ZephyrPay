#!/usr/bin/env python3
"""
ZephyrPay Coverage Standards Verification Tool

This tool verifies that code meets ZephyrPay Coding Standards V1.1 requirements:
- 90% minimum overall coverage
- 95% minimum coverage for security-critical components

Usage:
    python verify_coverage_standards.py [--auth-only] [--fix-issues]

Options:
    --auth-only     Check only auth endpoints (faster for auth-specific work)
    --fix-issues    Attempt to automatically fix coverage issues by generating test templates
"""

import os
import sys
import subprocess
import argparse
import glob
import xml.etree.ElementTree as ET
from pathlib import Path

# ZephyrPay Coding Standards V1.1 thresholds
OVERALL_THRESHOLD = 90.0
SECURITY_THRESHOLD = 95.0

# Security-critical components
SECURITY_COMPONENTS = [
    "app.api.v1.endpoints.auth",
    "app.core.security",
    "app.api.v1.endpoints.roles",
    "app.core.rbac"
]

def set_environment():
    """Set up testing environment variables"""
    os.environ.update({
        "DATABASE_URL": "sqlite:///./test.db",
        "SECRET_KEY": "testingsecretkey",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "11520",
        "TESTING": "True",
        "PYTHONPATH": str(Path(__file__).resolve().parent.parent)
    })
    
    # Ensure test database exists
    repo_root = Path(__file__).resolve().parent.parent
    test_db_dir = repo_root / "backend" / "app" / "tests" / "data"
    test_db_dir.mkdir(parents=True, exist_ok=True)
    
    test_db_path = test_db_dir / "test.db"
    if not test_db_path.exists():
        test_db_path.touch()

def run_tests(auth_only=False):
    """Run tests with coverage measurement"""
    print("\n=== Running tests with coverage measurement ===")
    
    repo_root = Path(__file__).resolve().parent.parent
    backend_dir = repo_root / "backend"
    
    # Pre-import critical modules to ensure proper instrumentation
    print("\nPre-importing modules to ensure proper coverage tracking...")
    preimport_cmd = [
        sys.executable,
        "-c",
        "import sys; sys.path.insert(0, '.'); "
        "from app.api.v1.endpoints import auth; "
        "print(f'Auth module loaded: {auth.__file__}')"
    ]
    subprocess.run(preimport_cmd, cwd=str(backend_dir))
    
    # Determine which tests to run
    if auth_only:
        test_pattern = "app/tests/api/v1/test_auth*.py"
        source_arg = "--cov=app.api.v1.endpoints.auth"
    else:
        test_pattern = "app/tests"
        source_arg = "--cov=app"
    
    # Run pytest with coverage
    pytest_cmd = [
        sys.executable, "-m", "pytest",
        test_pattern, "-v",
        source_arg,
        "--cov-report=xml",
        "--cov-report=term"
    ]
    
    print(f"\nRunning: {' '.join(pytest_cmd)}")
    result = subprocess.run(
        pytest_cmd,
        cwd=str(backend_dir),
        capture_output=True,
        text=True
    )
    
    # Show test results
    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        print("\nTest output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
    
    # Check if coverage report was generated
    coverage_xml = backend_dir / "coverage.xml"
    if coverage_xml.exists():
        print(f"\nCoverage report generated at {coverage_xml}")
        return str(coverage_xml)
    else:
        print("\n❌ No coverage report generated!")
        return None

def analyze_coverage(coverage_file):
    """Analyze coverage report against ZephyrPay standards"""
    if not os.path.exists(coverage_file):
        print(f"Error: Coverage file {coverage_file} not found")
        return False
    
    try:
        tree = ET.parse(coverage_file)
        root = tree.getroot()
        
        # Get overall coverage
        overall = float(root.attrib.get('line-rate', 0)) * 100
        print(f"\n=== ZephyrPay Coverage Standards Analysis ===")
        print(f"Overall coverage: {overall:.2f}%")
        
        # Check overall threshold
        if overall >= OVERALL_THRESHOLD:
            print(f"✅ Overall coverage meets ZephyrPay's {OVERALL_THRESHOLD}% requirement")
            overall_pass = True
        else:
            print(f"❌ Overall coverage below ZephyrPay's {OVERALL_THRESHOLD}% requirement")
            overall_pass = False
        
        # Check security-critical components
        print("\nSecurity-Critical Components:")
        security_found = False
        all_security_passed = True
        security_components_data = []
        
        for package in root.findall(".//package"):
            pkg_name = package.attrib.get('name', '')
            is_security = False
            
            for security_component in SECURITY_COMPONENTS:
                if security_component in pkg_name:
                    is_security = True
                    security_found = True
                    break
            
            # Calculate coverage for this package
            line_rate = float(package.attrib.get('line-rate', 0)) * 100
            lines_valid = int(package.attrib.get('lines-valid', 0))
            lines_covered = int(line_rate/100 * lines_valid)
            
            # Store component info for reporting
            component_data = {
                'name': pkg_name,
                'is_security': is_security,
                'coverage': line_rate,
                'lines_valid': lines_valid,
                'lines_covered': lines_covered,
                'missing_lines': []
            }
            
            # Collect uncovered lines for security components
            if is_security:
                for class_elem in package.findall(".//class"):
                    filename = class_elem.attrib.get('filename', '')
                    for line in class_elem.findall(".//line"):
                        if int(line.attrib.get('hits', 0)) == 0:
                            line_num = line.attrib.get('number', '?')
                            component_data['missing_lines'].append(f"{filename}:{line_num}")
            
            security_components_data.append(component_data)
        
        # Report on security components
        low_coverage_components = []
        for component in security_components_data:
            if component['is_security']:
                # Evaluate against security threshold
                meets_threshold = component['coverage'] >= SECURITY_THRESHOLD
                if not meets_threshold:
                    all_security_passed = False
                    low_coverage_components.append(component)
                
                # Report status
                status = "✅" if meets_threshold else "❌"
                print(f"{status} {component['name']}: {component['coverage']:.2f}% ({component['lines_covered']}/{component['lines_valid']} lines)")
                
        if not security_found:
            print("⚠️ No security-critical components found in coverage report!")
            all_security_passed = False
        elif all_security_passed:
            print(f"\n✅ All security-critical components meet the {SECURITY_THRESHOLD}% requirement")
        else:
            print(f"\n❌ Some security-critical components below {SECURITY_THRESHOLD}% requirement")
        
        # Detailed report on failing components
        if low_coverage_components:
            print("\n=== Missing Coverage Details ===")
            for component in low_coverage_components:
                print(f"\n{component['name']} - {component['coverage']:.2f}%")
                print(f"Missing {component['lines_valid'] - component['lines_covered']} of {component['lines_valid']} lines")
                
                if component['missing_lines']:
                    print("\nUncovered lines:")
                    for line in component['missing_lines'][:10]:  # Show first 10
                        print(f"  - {line}")
                    
                    if len(component['missing_lines']) > 10:
                        print(f"  ... and {len(component['missing_lines']) - 10} more")
                
                # BDD-style testing suggestion
                print("\nSuggested test improvements (BDD-style):")
                print("  1. Write failing tests for uncovered code paths (Red stage)")
                print("  2. Implement the functionality to make tests pass (Green stage)")
                print("  3. Refactor while maintaining passing tests")
        
        # Return overall result
        return overall_pass and all_security_passed
        
    except Exception as e:
        print(f"Error analyzing coverage: {str(e)}")
        return False

def generate_missing_tests(coverage_file, auth_only=True):
    """Generate test templates for missing coverage"""
    if not os.path.exists(coverage_file):
        print("Cannot generate tests: coverage file not found")
        return False
    
    try:
        tree = ET.parse(coverage_file)
        root = tree.getroot()
        
        components_to_fix = []
        for package in root.findall(".//package"):
            pkg_name = package.attrib.get('name', '')
            
            # Filter by auth components if auth_only is True
            if auth_only and 'auth' not in pkg_name:
                continue
                
            line_rate = float(package.attrib.get('line-rate', 0)) * 100
            is_security = any(sec in pkg_name for sec in SECURITY_COMPONENTS)
            threshold = SECURITY_THRESHOLD if is_security else OVERALL_THRESHOLD
            
            if line_rate < threshold:
                components_to_fix.append({
                    'name': pkg_name,
                    'coverage': line_rate,
                    'is_security': is_security,
                    'classes': []
                })
                
                # Collect class-level info
                for class_elem in package.findall(".//class"):
                    class_name = class_elem.attrib.get('name', '')
                    filename = class_elem.attrib.get('filename', '')
                    
                    missing_lines = []
                    for line in class_elem.findall(".//line"):
                        if int(line.attrib.get('hits', 0)) == 0:
                            missing_lines.append(int(line.attrib.get('number', 0)))
                    
                    if missing_lines:
                        components_to_fix[-1]['classes'].append({
                            'name': class_name,
                            'filename': filename,
                            'missing_lines': missing_lines
                        })
        
        # Generate test templates
        if components_to_fix:
            print("\n=== Generating Test Templates ===")
            
            repo_root = Path(__file__).resolve().parent.parent
            backend_dir = repo_root / "backend"
            
            for component in components_to_fix:
                print(f"\nComponent: {component['name']} ({component['coverage']:.2f}%)")
                
                for cls in component['classes']:
                    # Create BDD-style test template
                    module_path = cls['name'].split('.')
                    test_name = f"test_complete_coverage_{module_path[-1]}.py"
                    
                    # Determine appropriate test directory
                    if 'api.v1.endpoints' in cls['name']:
                        test_dir = backend_dir / "app" / "tests" / "api" / "v1"
                    elif 'core' in cls['name']:
                        test_dir = backend_dir / "app" / "tests" / "core"
                    elif 'services' in cls['name']:
                        test_dir = backend_dir / "app" / "tests" / "services"
                    else:
                        test_dir = backend_dir / "app" / "tests"
                    
                    test_dir.mkdir(parents=True, exist_ok=True)
                    test_file = test_dir / test_name
                    
                    if not test_file.exists():
                        with open(test_file, 'w') as f:
                            f.write(f'''"""
BDD-style tests for complete coverage of {cls['name']}

Following ZephyrPay Coding Standards V1.1:
- Test-Driven Development approach
- Comprehensive coverage of all code paths
- Focus on security and edge cases
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

# Import the module being tested
# from {".".join(module_path[:-1])} import {module_path[-1]}

class Test{module_path[-1].title().replace("_", "")}CompleteCoverage:
    """
    Feature: Complete Coverage for {module_path[-1]}
    As a developer
    I want to ensure all code paths are tested
    So that I meet ZephyrPay's coverage standards
    """
    
    def test_uncovered_paths(self, client: TestClient):
        """
        Scenario: Coverage for previously untested paths
        Given I have identified lines {cls['missing_lines'][:5]}
        When I execute those code paths
        Then the test coverage should increase
        """
        # TODO: Implement test to cover missing lines
        pass
    
    def test_edge_cases(self):
        """
        Scenario: Edge case handling
        Given I have identified edge cases
        When I test those specific scenarios
        Then all exception paths should be covered
        """
        # TODO: Implement test for edge cases
        pass
''')
                        print(f"Created test template: {test_file}")
            
            print("\n✅ Test templates generated successfully")
            print("\nNext steps:")
            print("1. Implement the failing tests (Red)")
            print("2. Fix the code to make tests pass (Green)")
            print("3. Refactor while keeping tests passing")
            print("4. Run this tool again to verify coverage")
            
            return True
        else:
            print("No components need fixing")
            return False
            
    except Exception as e:
        print(f"Error generating test templates: {str(e)}")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="ZephyrPay Coverage Standards Verification")
    parser.add_argument("--auth-only", action="store_true", help="Check only auth endpoints")
    parser.add_argument("--fix-issues", action="store_true", help="Generate test templates for missing coverage")
    args = parser.parse_args()
    
    # Set up environment
    set_environment()
    
    # Run tests
    coverage_file = run_tests(auth_only=args.auth_only)
    
    if coverage_file:
        # Analyze coverage
        meets_standards = analyze_coverage(coverage_file)
        
        # Generate tests for missing coverage if requested
        if args.fix_issues and not meets_standards:
            generate_missing_tests(coverage_file, auth_only=args.auth_only)
        
        # Final result
        print("\n=== Coverage Verification Results ===")
        if meets_standards:
            print("✅ Code meets ZephyrPay coverage standards")
            return 0
        else:
            print("❌ Code does not meet ZephyrPay coverage standards")
            print("   Run with --fix-issues to generate test templates")
            return 1
    else:
        print("❌ Failed to generate coverage report")
        return 1

if __name__ == "__main__":
    sys.exit(main())
