#!/usr/bin/env python
"""
Auth Coverage Enforcer

This script enforces the 95% coverage requirement for auth endpoints
as specified in ZephyrPay's Coding Standards V1.1.

It ensures that all security-critical components, particularly
authentication endpoints, maintain high test coverage.
"""

import os
import sys
import importlib
import importlib.util
import coverage
import pytest
from pathlib import Path
import xml.etree.ElementTree as ET

# Set up proper paths for Python imports
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(BACKEND_DIR))

# Required coverage percentage for auth endpoints
REQUIRED_COVERAGE = 95.0

def handle_imports():
    """Add necessary paths for imports to work in any environment"""
    # Print current environment for debugging
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    
    # Try different import approaches
    try:
        # First attempt: Direct backend import
        import backend.app.api.v1.endpoints.auth
        print("✅ Successfully imported auth module via 'backend.app' path")
        return True
    except ImportError as e:
        print(f"❌ Direct import failed: {str(e)}")
        
        # Second attempt: Try relative path
        try:
            sys.path.insert(0, str(BACKEND_DIR))
            from app.api.v1.endpoints import auth
            print("✅ Successfully imported auth module via 'app' path")
            return True
        except ImportError as e:
            print(f"❌ Relative import failed: {str(e)}")
            
            # Third attempt: Try direct file import
            try:
                auth_path = os.path.join(BACKEND_DIR, "app", "api", "v1", "endpoints", "auth.py")
                if not os.path.exists(auth_path):
                    print(f"❌ Auth file not found at: {auth_path}")
                    return False
                    
                print(f"✅ Auth file found at: {auth_path}")
                return True
            except Exception as e:
                print(f"❌ File check failed: {str(e)}")
                return False

def initialize_auth_module():
    """Initialize auth module for coverage tracking"""
    print("Initializing auth module for coverage tracking...")
    
    # Set up environment for testing
    os.environ["TESTING"] = "True"
    os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
    os.environ.setdefault("SECRET_KEY", "testingsecretkey")
    os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "11520")
    
    # Remove any environment variables that might cause validation errors
    if "GITHUB_TOKEN" in os.environ:
        del os.environ["GITHUB_TOKEN"]
        
    # Check for auth module
    auth_module_path = BACKEND_DIR / "app" / "api" / "v1" / "endpoints" / "auth.py"
    print(f"Auth module path: {auth_module_path}")
    
    if not auth_module_path.exists():
        print(f"Error: Auth module not found at {auth_module_path}")
        return False
    
    # Import auth module
    try:
        # Use importlib to load module from file path
        spec = importlib.util.spec_from_file_location("auth", str(auth_module_path))
        auth_module = importlib.util.module_from_spec(spec)
        
        # Add the backend directory to sys.path to resolve imports within the auth module
        backend_parent = str(BACKEND_DIR.parent)
        if backend_parent not in sys.path:
            sys.path.insert(0, backend_parent)
            
        # Add the app directory to sys.path
        app_dir = str(BACKEND_DIR)
        if app_dir not in sys.path:
            sys.path.insert(0, app_dir)
            
        # Execute the module
        spec.loader.exec_module(auth_module)
        
        # Print routes for verification
        print(f"Auth router paths: {[route.path for route in auth_module.router.routes]}")
        for route in auth_module.router.routes:
            print(f"Route: {route.path}, Methods: {route.methods}")
            print(f"Endpoint: {route.endpoint.__name__}")
            
        print("Testing auth error handling")
        return auth_module
    except Exception as e:
        print(f"Error initializing auth module: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def run_tests_with_coverage():
    """Run auth endpoint tests with coverage measurement"""
    print("\nRunning tests with coverage measurement...")
    
    # Set up environment again for test run
    os.environ["TESTING"] = "True"
    os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
    os.environ.setdefault("SECRET_KEY", "testingsecretkey")
    os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "11520")
    
    # Remove any environment variables that might cause validation errors
    if "GITHUB_TOKEN" in os.environ:
        del os.environ["GITHUB_TOKEN"]
    
    # Initialize auth module again
    auth_module = initialize_auth_module()
    if not auth_module:
        return False
    
    # Create and configure coverage object with absolute paths
    auth_module_path = os.path.join(BACKEND_DIR, "app", "api", "v1", "endpoints", "auth.py")
    cov = coverage.Coverage(
        source=[auth_module_path],  # Use absolute file path instead of module path
        branch=True,
        data_file='.auth_coverage',
        config_file=False,
        include=["**/auth.py"],  # Only include auth.py files
        omit=['**/__pycache__/*', '**/.venv/*', '**/tests/*']
    )
    
    try:
        # Start coverage
        cov.start()
        
        # Find test file
        test_file = BACKEND_DIR / "app" / "tests" / "api" / "v1" / "test_auth_complete_coverage.py"
        if not test_file.exists():
            print(f"Error: Test file not found at {test_file}")
            return False
        
        # Run tests with importlib mode to handle imports properly
        result = pytest.main([
            str(test_file),
            "-v",
            "--import-mode=importlib"
        ])
        
        # Check if tests passed
        if result != 0:
            print("Error: Tests failed")
            return False
    finally:
        # Stop coverage
        cov.stop()
        cov.save()
    
    # Generate reports
    try:
        print("Generating coverage reports...")
        coverage_percentage = cov.report()
        cov.xml_report(outfile='auth_coverage.xml')
        cov.html_report(directory='auth_coverage_html')
        
        # Check if coverage meets requirement
        if coverage_percentage >= REQUIRED_COVERAGE:
            print(f"✅ Auth endpoint coverage: {coverage_percentage:.2f}% meets requirement of {REQUIRED_COVERAGE}%")
            
            # Parse existing XML file to get the actual coverage
            try:
                tree = ET.parse('auth_coverage.xml')
                root = tree.getroot()
                package = root.find('.//package[@name="backend.app.api.v1.endpoints"]')
                if package is not None:
                    auth_class = package.find('.//class[@name="auth.py"]')
                    if auth_class is not None:
                        line_rate = float(auth_class.get('line-rate', '0'))
                        xml_coverage = line_rate * 100
                        print(f"XML reports coverage: {xml_coverage:.2f}%")
                        return True if xml_coverage >= REQUIRED_COVERAGE else False
            except Exception as e:
                print(f"Error parsing XML coverage: {str(e)}")
                
            return True
        else:
            print(f"❌ Auth endpoint coverage: {coverage_percentage:.2f}% does not meet requirement of {REQUIRED_COVERAGE}%")
            return False
    except Exception as e:
        print(f"Error generating coverage report: {str(e)}")
        
        # Fall back to XML parsing if direct coverage fails
        try:
            print("✅ Coverage XML file found at auth_coverage.xml")
            tree = ET.parse('auth_coverage.xml')
            root = tree.getroot()
            package = root.find('.//package[@name="backend.app.api.v1.endpoints"]')
            if package is not None:
                auth_class = package.find('.//class[@name="auth.py"]')
                if auth_class is not None:
                    line_rate = float(auth_class.get('line-rate', '0'))
                    xml_coverage = line_rate * 100
                    print(f"XML reports coverage: {xml_coverage:.2f}%")
                    return xml_coverage >= REQUIRED_COVERAGE
                    
            print("❌ Could not find auth module coverage in XML file")
            return False
        except Exception as xml_error:
            print(f"Error parsing XML coverage: {str(xml_error)}")
            return False

def main():
    """Main function"""
    # First check import handling
    if not handle_imports():
        print("❌ Import handling setup failed")
        return 1
    
    # Run tests with coverage
    if run_tests_with_coverage():
        print("\n✅ Auth coverage check passed")
        return 0
    else:
        print("\n❌ Auth coverage check failed")
        
        # Check if XML file was generated
        xml_path = Path('auth_coverage.xml')
        if not xml_path.exists():
            print(f"❌ Error: Coverage XML file not found at {xml_path}")
        else:
            print(f"✅ Coverage XML file found at {xml_path}")
            # Try to parse the XML file
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                # Get coverage information
                line_rate = float(root.attrib.get('line-rate', '0'))
                coverage_percentage = line_rate * 100
                print(f"XML reports coverage: {coverage_percentage:.2f}%")
            except Exception as e:
                print(f"❌ Error parsing XML file: {str(e)}")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
