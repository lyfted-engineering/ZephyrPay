#!/usr/bin/env python3
"""
Verify overall coverage report for ZephyrPay

This script analyzes a coverage XML report to check if
security-critical components meet the 95% coverage
requirement according to ZephyrPay's Coding Standards V1.1
"""

import sys
import os
import xml.etree.ElementTree as ET

def verify_coverage(coverage_file):
    try:
        # Parse the coverage XML report
        if not os.path.exists(coverage_file):
            print('❌ Coverage file not found')
            sys.exit(1)
            
        tree = ET.parse(coverage_file)
        root = tree.getroot()
    
        # Get overall coverage
        overall_coverage = float(root.attrib.get('line-rate', 0)) * 100
        print(f'Overall coverage: {overall_coverage:.2f}%')
    
        # Check coverage for security-critical packages
        security_critical = [
            'app.api.v1.endpoints.auth', 
            'app.core.security', 
            'app.api.v1.endpoints.roles',
            'app.core.rbac'
        ]
        
        # Find all packages in coverage report
        print('\nPackages found in coverage report:')
        found_packages = []
        for package in root.findall('.//package'):
            pkg_name = package.attrib.get('name', '')
            coverage_rate = float(package.attrib.get('line-rate', 0)) * 100
            found_packages.append((pkg_name, coverage_rate))
            print(f'- {pkg_name}: {coverage_rate:.2f}%')
            
        print('\nSecurity-critical packages:')
        security_critical_found = False
        security_critical_met = True
        
        for pkg in security_critical:
            for found_pkg, coverage_rate in found_packages:
                if pkg in found_pkg:
                    security_critical_found = True
                    print(f'- {found_pkg}: {coverage_rate:.2f}%')
                    
                    # Check if it meets 95% requirement
                    if coverage_rate < 95.0:
                        security_critical_met = False
                        print(f'  ❌ BELOW REQUIRED 95% THRESHOLD')
                    else:
                        print(f'  ✅ Meets 95% requirement')
                    
        if not security_critical_found:
            print('❌ No security-critical packages found in coverage report')
            return 1
            
        # Output final result
        if security_critical_met:
            print('\n✅ All security-critical packages meet ZephyrPay\'s 95% coverage requirement')
            return 0
        else:
            print('\n❌ Some security-critical packages do not meet ZephyrPay\'s 95% coverage requirement')
            return 1
                
    except Exception as e:
        print(f'❌ Error analyzing coverage: {str(e)}')
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: verify_overall_coverage.py <coverage_xml_file>')
        sys.exit(1)
        
    coverage_file = sys.argv[1]
    exit_code = verify_coverage(coverage_file)
    sys.exit(exit_code)
