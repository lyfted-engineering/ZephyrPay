#!/usr/bin/env python3
"""
ZephyrPay Auth Coverage Analyzer

This script analyzes test coverage for auth endpoints according to 
ZephyrPay Coding Standards V1.1 requirements:
- 90% minimum overall coverage
- 95% minimum coverage for security-critical components
"""

import os
import sys
import glob
import subprocess
import xml.etree.ElementTree as ET

# Security-critical requirements from ZephyrPay Standards V1.1
SECURITY_THRESHOLD = 95
OVERALL_THRESHOLD = 90

def main():
    """Main function to run auth coverage analysis"""
    # Set environment variables for testing
    os.environ.update({
        "DATABASE_URL": "sqlite:///./test.db",
        "SECRET_KEY": "testingsecretkey",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "11520",
        "TESTING": "True",
        "PYTHONPATH": os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    })
    
    # Ensure test database exists
    data_dir = os.path.join("app", "tests", "data")
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, "test.db")
    if not os.path.exists(db_path):
        with open(db_path, "w") as f:
            pass
    
    # Find all auth test files
    test_dir = os.path.join("app", "tests", "api", "v1")
    test_files = glob.glob(os.path.join(test_dir, "test_auth*.py"))
    
    if not test_files:
        print(f"No auth test files found in {test_dir}")
        return False
    
    print(f"Found {len(test_files)} auth test files:")
    for test_file in test_files:
        print(f"  - {test_file}")
    
    # Pre-import the auth module
    print("\nPre-importing auth module...")
    preimport_cmd = [
        sys.executable,
        "-c",
        "from app.api.v1.endpoints import auth; print(f'Auth module loaded from {auth.__file__}')"
    ]
    subprocess.run(preimport_cmd)
    
    # Clean existing coverage data
    if os.path.exists(".coverage"):
        os.remove(".coverage")
    
    # Run tests with coverage
    print("\nRunning tests with coverage...")
    coverage_cmd = [
        sys.executable,
        "-m", "coverage", "run",
        "--source=app.api.v1.endpoints.auth",
        "-m", "pytest"
    ] + test_files + ["-v"]
    
    process = subprocess.run(coverage_cmd, capture_output=True, text=True)
    
    # Show test results
    print("\nTest execution completed.")
    if process.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        # Show error details
        print("\nTest output:")
        print(process.stdout)
        if process.stderr:
            print("\nErrors:")
            print(process.stderr)
        return False
    
    # Generate coverage reports
    print("\nGenerating coverage reports...")
    subprocess.run([sys.executable, "-m", "coverage", "report", "-m"])
    subprocess.run([sys.executable, "-m", "coverage", "xml"])
    
    # Analyze coverage
    analyze_coverage()
    return True

def analyze_coverage():
    """Analyze coverage report against ZephyrPay standards"""
    if not os.path.exists("coverage.xml"):
        print("❌ No coverage report generated!")
        return
    
    try:
        # Parse coverage XML report
        tree = ET.parse("coverage.xml")
        root = tree.getroot()
        
        # Get overall coverage
        overall = float(root.attrib.get("line-rate", 0)) * 100
        print(f"\n=== Coverage Analysis ===")
        print(f"Overall coverage: {overall:.2f}%")
        
        # Check against ZephyrPay standards
        if overall >= OVERALL_THRESHOLD:
            print(f"✅ Meets ZephyrPay's overall coverage requirement of {OVERALL_THRESHOLD}%")
        else:
            print(f"❌ Below ZephyrPay's overall coverage requirement of {OVERALL_THRESHOLD}%")
        
        # Check security-critical components
        print("\nSecurity-Critical Components:")
        for package in root.findall(".//package"):
            pkg_name = package.attrib.get("name", "")
            
            if "app.api.v1.endpoints.auth" in pkg_name:
                line_rate = float(package.attrib.get("line-rate", 0)) * 100
                lines_valid = int(package.attrib.get("lines-valid", 0))
                lines_covered = int(float(package.attrib.get("line-rate", 0)) * lines_valid)
                
                # Check against security threshold
                if line_rate >= SECURITY_THRESHOLD:
                    print(f"✅ {pkg_name}: {line_rate:.2f}% ({lines_covered}/{lines_valid} lines)")
                else:
                    print(f"❌ {pkg_name}: {line_rate:.2f}% ({lines_covered}/{lines_valid} lines)")
                    print(f"   Below ZephyrPay's security component requirement of {SECURITY_THRESHOLD}%")
                
                # Look at specific files
                print("\nDetailed Module Coverage:")
                for class_element in package.findall(".//class"):
                    filename = class_element.attrib.get("name", "")
                    file_line_rate = float(class_element.attrib.get("line-rate", 0)) * 100
                    file_lines = int(class_element.attrib.get("lines-valid", 0))
                    covered = int(float(class_element.attrib.get("line-rate", 0)) * file_lines)
                    
                    status = "✅" if file_line_rate >= SECURITY_THRESHOLD else "❌"
                    print(f"{status} {filename}: {file_line_rate:.2f}% ({covered}/{file_lines} lines)")
                
                # Identify any uncovered lines
                print("\nUncovered Lines (if any):")
                has_uncovered = False
                for class_element in package.findall(".//class"):
                    filename = class_element.attrib.get("name", "")
                    for line in class_element.findall(".//line"):
                        hits = int(line.attrib.get("hits", 0))
                        if hits == 0:
                            has_uncovered = True
                            line_num = line.attrib.get("number", "?")
                            print(f"  - {filename}:{line_num}")
                
                if not has_uncovered:
                    print("  None! 100% line coverage achieved!")
    
    except Exception as e:
        print(f"Error analyzing coverage: {str(e)}")

if __name__ == "__main__":
    main()
