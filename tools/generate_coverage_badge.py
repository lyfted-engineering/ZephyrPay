#!/usr/bin/env python3
"""
ZephyrPay Coverage Badge Generator

This script analyzes a coverage XML report and generates a badge-compatible 
output that can be used in GitHub Actions to generate coverage badges.

Following ZephyrPay standards v1.1 which requires:
- 90% minimum overall coverage
- 95% minimum for security-critical components

Usage:
    python generate_coverage_badge.py [coverage_xml_path]
"""

import sys
import os
import xml.etree.ElementTree as ET
import json

# ZephyrPay standards from v1.1
OVERALL_THRESHOLD = 90
SECURITY_THRESHOLD = 95
SECURITY_COMPONENTS = [
    "app.api.v1.endpoints.auth",
    "app.core.security", 
    "app.api.v1.endpoints.roles",
    "app.core.rbac"
]

def generate_badge_data(coverage_file):
    """Generate badge data from coverage XML file"""
    if not os.path.exists(coverage_file):
        print(f"Error: Coverage file {coverage_file} not found")
        return {"schemaVersion": 1, "label": "coverage", "message": "N/A", "color": "red"}
    
    try:
        tree = ET.parse(coverage_file)
        root = tree.getroot()
        
        # Get overall coverage
        overall = float(root.attrib["line-rate"]) * 100
        
        # Check security components
        security_components = []
        security_total_lines = 0
        security_covered_lines = 0
        
        for package in root.findall(".//package"):
            pkg_name = package.attrib["name"]
            
            for critical in SECURITY_COMPONENTS:
                if critical in pkg_name:
                    lines = int(package.attrib.get("lines-valid", 0))
                    covered = int(package.attrib.get("lines-covered", 0))
                    coverage = (covered / lines * 100) if lines > 0 else 0
                    
                    security_components.append({
                        "name": pkg_name,
                        "coverage": coverage,
                        "lines": lines
                    })
                    
                    security_total_lines += lines
                    security_covered_lines += covered
                    break
        
        # Calculate security coverage
        security_coverage = 0
        if security_total_lines > 0:
            security_coverage = security_covered_lines / security_total_lines * 100
        
        # Determine color
        color = "red"
        if overall >= 90:
            color = "brightgreen"
        elif overall >= 80:
            color = "green"
        elif overall >= 70:
            color = "yellowgreen"
        elif overall >= 60:
            color = "yellow"
        elif overall >= 50:
            color = "orange"
        
        # Create badge data
        badge_data = {
            "schemaVersion": 1,
            "label": "coverage",
            "message": f"{overall:.1f}%",
            "color": color
        }
        
        # Additional data for GitHub workflow
        print(f"::set-output name=coverage::{overall:.1f}")
        
        if security_components:
            print(f"::set-output name=security_coverage::{security_coverage:.1f}")
            
            meets_standard = overall >= OVERALL_THRESHOLD and security_coverage >= SECURITY_THRESHOLD
            print(f"::set-output name=meets_standard::{str(meets_standard).lower()}")
            
            security_status = []
            for comp in security_components:
                status = "✓" if comp["coverage"] >= SECURITY_THRESHOLD else "✗"
                security_status.append(f"{status} {comp['name']}: {comp['coverage']:.1f}%")
            
            print("\nSecurity Component Coverage:")
            for status in security_status:
                print(status)
        else:
            print("\nWarning: No security components found in coverage report")
        
        return badge_data
        
    except Exception as e:
        print(f"Error processing coverage: {str(e)}")
        return {"schemaVersion": 1, "label": "coverage", "message": "error", "color": "red"}

def main():
    """Main function"""
    coverage_file = "backend/coverage.xml"
    if len(sys.argv) > 1:
        coverage_file = sys.argv[1]
    
    badge_data = generate_badge_data(coverage_file)
    
    # Print badge data to stdout
    print(f"\nOverall Coverage: {badge_data['message']}")
    print(json.dumps(badge_data, indent=2))

if __name__ == "__main__":
    main()
