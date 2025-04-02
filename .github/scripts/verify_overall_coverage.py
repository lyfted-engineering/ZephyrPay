#!/usr/bin/env python3
"""
Verify overall coverage report for ZephyrPay

This script analyzes a coverage XML report to check if
security-critical components meet the coverage requirements
according to ZephyrPay's Coding Standards V1.1:
- 95% for security-critical components
- 90% for all other components
"""

import sys
import os
import xml.etree.ElementTree as ET

# Default coverage thresholds as per ZephyrPay standards
DEFAULT_OVERALL_THRESHOLD = 90.0
SECURITY_CRITICAL_THRESHOLD = 95.0

def verify_coverage(coverage_file, overall_threshold=DEFAULT_OVERALL_THRESHOLD):
    """
    Verify coverage in a coverage XML file against ZephyrPay standards.
    
    Args:
        coverage_file: Path to the coverage XML file
        overall_threshold: Minimum required overall coverage percentage (default: 90%)
    
    Returns:
        True if coverage meets the requirements, False otherwise
    """
    try:
        # Parse the coverage XML report
        if not os.path.exists(coverage_file):
            print('❌ Coverage file not found')
            return False
            
        tree = ET.parse(coverage_file)
        root = tree.getroot()
    
        # Get overall coverage
        overall_coverage = float(root.attrib.get('line-rate', 0)) * 100
        print(f'Overall coverage: {overall_coverage:.2f}%')
        
        # Check if overall coverage meets the threshold
        overall_meets_threshold = overall_coverage >= overall_threshold
        if overall_meets_threshold:
            print(f'✅ Overall coverage meets the {overall_threshold:.1f}% requirement')
        else:
            print(f'❌ Overall coverage ({overall_coverage:.2f}%) is below the {overall_threshold:.1f}% requirement')
    
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
            pkg_found = False
            for found_pkg, coverage_rate in found_packages:
                if pkg in found_pkg:
                    pkg_found = True
                    security_critical_found = True
                    if coverage_rate < SECURITY_CRITICAL_THRESHOLD:
                        security_critical_met = False
                        print(f'❌ {pkg}: {coverage_rate:.2f}% (below {SECURITY_CRITICAL_THRESHOLD:.1f}% requirement)')
                    else:
                        print(f'✅ {pkg}: {coverage_rate:.2f}% (meets {SECURITY_CRITICAL_THRESHOLD:.1f}% requirement)')
                    break
            if not pkg_found:
                print(f'⚠️ {pkg}: Not found in coverage report')
        
        if not security_critical_found:
            print('⚠️ No security-critical packages found in coverage report')
            return overall_meets_threshold
        
        if security_critical_met:
            print(f'\n✅ All security-critical packages meet the {SECURITY_CRITICAL_THRESHOLD:.1f}% coverage requirement')
        else:
            print(f'\n❌ Some security-critical packages do not meet the {SECURITY_CRITICAL_THRESHOLD:.1f}% coverage requirement')
            
        # Return True only if both overall and security-critical coverage requirements are met
        return overall_meets_threshold and security_critical_met
    
    except Exception as e:
        print(f'❌ Error analyzing coverage report: {str(e)}')
        return False

if __name__ == '__main__':
    # Check arguments
    if len(sys.argv) < 2:
        print('Usage: verify_overall_coverage.py <coverage_xml_file> [overall_threshold]')
        sys.exit(1)
    
    # Get coverage file path from command line arguments
    coverage_file = sys.argv[1]
    
    # Get threshold from command line arguments (optional)
    threshold = DEFAULT_OVERALL_THRESHOLD
    if len(sys.argv) >= 3:
        try:
            threshold = float(sys.argv[2])
        except ValueError:
            print(f'❌ Invalid threshold value: {sys.argv[2]}. Using default: {DEFAULT_OVERALL_THRESHOLD}%')
    
    # Verify coverage
    print(f'Verifying coverage against ZephyrPay standards:')
    print(f'- Overall threshold: {threshold:.1f}%')
    print(f'- Security-critical threshold: {SECURITY_CRITICAL_THRESHOLD:.1f}%')
    
    if verify_coverage(coverage_file, threshold):
        print('\n✅ Coverage meets ZephyrPay standards')
        sys.exit(0)
    else:
        print('\n❌ Coverage does not meet ZephyrPay standards')
        sys.exit(1)
