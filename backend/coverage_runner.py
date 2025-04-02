#!/usr/bin/env python3
"""
ZephyrPay Coverage Runner

This script runs the auth tests with proper coverage measurement
following ZephyrPay Coding Standards V1.1 requirements:
- 90% minimum overall coverage
- 95% minimum for security-critical components

For direct instrumentation without pytest-cov import issues
"""

import os
import sys
import subprocess
import xml.etree.ElementTree as ET

# Security component thresholds from ZephyrPay Coding Standards V1.1
OVERALL_THRESHOLD = 90
SECURITY_THRESHOLD = 95
SECURITY_COMPONENTS = [
    "app.api.v1.endpoints.auth",
    "app.core.security", 
    "app.api.v1.endpoints.roles",
    "app.core.rbac"
]

def run_auth_tests():
    """Run auth tests with coverage instrumentation"""
    # Get the current directory (backend)
    repo_root = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure proper PYTHONPATH
    os.environ["PYTHONPATH"] = os.path.dirname(repo_root)
    
    # Ensure we have a test database
    test_db_dir = os.path.join(repo_root, "app", "tests", "data")
    os.makedirs(test_db_dir, exist_ok=True)
    
    test_db_path = os.path.join(test_db_dir, "test.db")
    if not os.path.exists(test_db_path):
        with open(test_db_path, "w") as f:
            pass
    
    # Set environment variables for testing
    os.environ.update({
        "DATABASE_URL": "sqlite:///./test.db",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "11520",
        "SECRET_KEY": "testingsecretkey",
        "TESTING": "True"
    })
    
    # Step 1: Remove any existing coverage data
    try:
        os.remove(".coverage")
    except FileNotFoundError:
        pass
    
    # Step 2: First make sure the auth module is imported
    print("Pre-importing auth module to ensure it's tracked...")
    import_command = [
        sys.executable,
        "-c",
        "import sys; sys.path.insert(0, '.'); from app.api.v1.endpoints import auth; print(f'Auth module imported from {auth.__file__}')"
    ]
    subprocess.run(import_command, check=False)
    
    # Step 3: Run tests with coverage
    print("\nRunning tests with coverage instrumentation...")
    test_path = os.path.join(repo_root, "app", "tests", "api", "v1")
    test_pattern = "test_auth*.py"
    
    cmd = [
        sys.executable, 
        "-m", "coverage", "run",
        "--source=app.api.v1.endpoints.auth",
        "-m", "pytest", 
        os.path.join(test_path, test_pattern), 
        "-v"
    ]
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Step 4: Generate coverage report
    print("\nTest Results:")
    # Print only key portions of the output
    test_output_lines = result.stdout.split("\n")
    if len(test_output_lines) > 10:
        # Print test summary
        print("\n".join(test_output_lines[:5]))
        print("...")
        print("\n".join(test_output_lines[-10:]))
    else:
        print(result.stdout)
    
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        return False

    print("\nGenerating coverage reports...")
    subprocess.run([sys.executable, "-m", "coverage", "report", "-m"])
    subprocess.run([sys.executable, "-m", "coverage", "xml"])
    
    if not os.path.exists("coverage.xml"):
        print("❌ Failed to generate coverage report")
        return False
    
    # Step 5: Analyze coverage results
    analyze_coverage()
    return True

def analyze_coverage():
    """Analyze coverage against ZephyrPay standards"""
    if not os.path.exists("coverage.xml"):
        print("❌ No coverage report found")
        return
    
    try:
        tree = ET.parse("coverage.xml")
        root = tree.getroot()
        
        # Get overall coverage
        overall = float(root.attrib.get("line-rate", 0)) * 100
        print(f"\n=== Coverage Analysis ===")
        print(f"Overall coverage: {overall:.2f}%")
        
        # Check overall threshold
        if overall < OVERALL_THRESHOLD:
            print(f"❌ Overall coverage {overall:.2f}% is below required {OVERALL_THRESHOLD}%")
        else:
            print(f"✅ Overall coverage {overall:.2f}% meets required {OVERALL_THRESHOLD}%")
        
        # Check security components
        print("\nSecurity-Critical Components:")
        security_found = False
        all_security_passed = True
        
        for package in root.findall(".//package"):
            pkg_name = package.attrib.get("name", "")
            
            for critical_component in SECURITY_COMPONENTS:
                if critical_component in pkg_name:
                    security_found = True
                    line_rate = float(package.attrib.get("line-rate", 0)) * 100
                    lines_valid = int(package.attrib.get("lines-valid", 0))
                    lines_covered = int(lines_valid * float(package.attrib.get("line-rate", 0)))
                    
                    status = "✅" if line_rate >= SECURITY_THRESHOLD else "❌"
                    if line_rate < SECURITY_THRESHOLD:
                        all_security_passed = False
                    
                    print(f"{status} {pkg_name}: {line_rate:.2f}% ({lines_covered}/{lines_valid} lines)")
        
        if not security_found:
            print("⚠️ No security-critical components found in coverage report!")
        elif all_security_passed:
            print(f"\n✅ All security-critical components meet required {SECURITY_THRESHOLD}%")
        else:
            print(f"\n❌ Some security-critical components are below required {SECURITY_THRESHOLD}%")
            
    except Exception as e:
        print(f"Error analyzing coverage: {str(e)}")
        
if __name__ == "__main__":
    run_auth_tests()
