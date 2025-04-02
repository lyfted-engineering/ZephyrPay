#!/usr/bin/env python3
"""
ZephyrPay Security Coverage Verification

This script verifies that auth endpoints meet ZephyrPay's Coding Standards V1.1:
- 95% minimum coverage for security-critical components like auth endpoints

Usage:
    python verify_security_coverage.py [coverage_xml_path]
"""

import sys
import os
import xml.etree.ElementTree as ET

# ZephyrPay standards from coding standards v1.1
SECURITY_THRESHOLD = 95.0
AUTH_MODULE = 'app.api.v1.endpoints.auth'

def verify_coverage(coverage_file="coverage.xml"):
    """Verify coverage against ZephyrPay standards"""
    if not os.path.exists(coverage_file):
        print(f"Error: Coverage file {coverage_file} not found")
        return False
    
    try:
        tree = ET.parse(coverage_file)
        root = tree.getroot()
        
        auth_found = False
        auth_coverage = 0.0
        
        print('Security component coverage:')
        
        for pkg in root.findall('.//package'):
            name = pkg.attrib.get('name', '')
            if AUTH_MODULE in name:
                auth_found = True
                line_rate = float(pkg.attrib.get('line-rate', 0)) * 100
                lines = int(pkg.attrib.get('lines-valid', 0))
                covered = int(line_rate/100 * lines)
                print(f'Auth module: {line_rate:.2f}% ({covered}/{lines} lines)')
                auth_coverage = line_rate
        
        if not auth_found:
            print('ERROR: Auth module not found in coverage report')
            return False
        
        # Verify against ZephyrPay standards
        if auth_coverage >= SECURITY_THRESHOLD:
            print(f'✅ Auth coverage ({auth_coverage:.2f}%) meets ZephyrPay security standard ({SECURITY_THRESHOLD}%)')
            return True
        else:
            print(f'❌ Auth coverage ({auth_coverage:.2f}%) below ZephyrPay security standard ({SECURITY_THRESHOLD}%)')
            return False
            
    except Exception as e:
        print(f'Error analyzing coverage: {str(e)}')
        return False

if __name__ == "__main__":
    coverage_file = "coverage.xml"
    if len(sys.argv) > 1:
        coverage_file = sys.argv[1]
    
    success = verify_coverage(coverage_file)
    sys.exit(0 if success else 1)
