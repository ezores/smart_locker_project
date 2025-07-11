#!/usr/bin/env python3
"""
Comprehensive Security Scanner for Smart Locker Project
Detects hardcoded secrets, weak passwords, and security vulnerabilities
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

class SecurityScanner:
    def __init__(self):
        self.issues = []
        self.severity_levels = {
            'CRITICAL': 4,
            'HIGH': 3,
            'MEDIUM': 2,
            'LOW': 1
        }
        
    def scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Scan a single file for security issues"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            # Check for hardcoded secrets
            secret_patterns = [
                (r'password["\']?\s*[:=]\s*["\']([^"\']{1,20})["\']', 'Hardcoded password'),
                (r'secret["\']?\s*[:=]\s*["\']([^"\']{1,50})["\']', 'Hardcoded secret'),
                (r'key["\']?\s*[:=]\s*["\']([^"\']{1,50})["\']', 'Hardcoded key'),
                (r'token["\']?\s*[:=]\s*["\']([^"\']{1,50})["\']', 'Hardcoded token'),
                (r'api_key["\']?\s*[:=]\s*["\']([^"\']{1,50})["\']', 'Hardcoded API key'),
                (r'SECRET_KEY["\']?\s*[:=]\s*["\']([^"\']{1,50})["\']', 'Hardcoded SECRET_KEY'),
                (r'JWT_SECRET_KEY["\']?\s*[:=]\s*["\']([^"\']{1,50})["\']', 'Hardcoded JWT_SECRET_KEY'),
            ]
            
            for pattern, description in secret_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        'type': 'HARDCODED_SECRET',
                        'severity': 'CRITICAL',
                        'description': description,
                        'line': line_num,
                        'code': lines[line_num - 1].strip(),
                        'file': file_path
                    })
            
            # Check for weak passwords
            weak_password_patterns = [
                (r'password["\']?\s*[:=]\s*["\'](admin123|student123|password|123456|qwerty)["\']', 'Weak password'),
                (r'password["\']?\s*[:=]\s*["\']([a-zA-Z0-9]{1,8})["\']', 'Potentially weak password'),
            ]
            
            for pattern, description in weak_password_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        'type': 'WEAK_PASSWORD',
                        'severity': 'HIGH',
                        'description': description,
                        'line': line_num,
                        'code': lines[line_num - 1].strip(),
                        'file': file_path
                    })
            
            # Check for SQL injection patterns
            sql_patterns = [
                (r'execute\s*\(\s*["\']([^"\']*\+[^"\']*)["\']', 'Potential SQL injection'),
                (r'query\s*\(\s*["\']([^"\']*\+[^"\']*)["\']', 'Potential SQL injection'),
            ]
            
            for pattern, description in sql_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        'type': 'SQL_INJECTION',
                        'severity': 'CRITICAL',
                        'description': description,
                        'line': line_num,
                        'code': lines[line_num - 1].strip(),
                        'file': file_path
                    })
            
            # Check for debug statements in production code (exclude test files)
            if not any(test_dir in file_path for test_dir in ['test', 'tests', 'backup']):
                debug_patterns = [
                    (r'print\s*\(', 'Debug print statement'),
                    (r'console\.log\s*\(', 'Debug console.log statement'),
                    (r'debugger;', 'Debugger statement'),
                ]
            else:
                debug_patterns = []
            
            for pattern, description in debug_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        'type': 'DEBUG_STATEMENT',
                        'severity': 'LOW',
                        'description': description,
                        'line': line_num,
                        'code': lines[line_num - 1].strip(),
                        'file': file_path
                    })
                    
        except Exception as e:
            issues.append({
                'type': 'SCAN_ERROR',
                'severity': 'MEDIUM',
                'description': f'Error scanning file: {str(e)}',
                'line': 0,
                'code': '',
                'file': file_path
            })
            
        return issues
    
    def scan_directory(self, directory: str, exclude_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Scan entire directory for security issues"""
        if exclude_patterns is None:
            exclude_patterns = [
                'node_modules', '.git', '__pycache__', '.venv', 'venv',
                '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.dylib',
                '*.log', '*.tmp', '*.temp', '*.cache'
            ]
        
        all_issues = []
        scanned_files = 0
        
        for root, dirs, files in os.walk(directory):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip excluded file patterns
                if any(pattern in file_path for pattern in exclude_patterns):
                    continue
                
                # Only scan text files
                if file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.yml', '.yaml', '.sh', '.md')):
                    issues = self.scan_file(file_path)
                    all_issues.extend(issues)
                    scanned_files += 1
        
        return {
            'issues': all_issues,
            'scanned_files': scanned_files,
            'total_issues': len(all_issues)
        }
    
    def generate_report(self, scan_results: Dict[str, Any]) -> str:
        """Generate a human-readable security report"""
        issues = scan_results['issues']
        scanned_files = scan_results['scanned_files']
        
        if not issues:
            return "No security issues found!"
        
        # Group issues by severity
        issues_by_severity = {}
        for issue in issues:
            severity = issue['severity']
            if severity not in issues_by_severity:
                issues_by_severity[severity] = []
            issues_by_severity[severity].append(issue)
        
        report = f"""
Security Scan Report
====================
Scanned Files: {scanned_files}
Total Issues: {len(issues)}

"""
        
        # Sort severities by importance
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            if severity in issues_by_severity:
                report += f"\n{severity} Issues ({len(issues_by_severity[severity])}):\n"
                report += "-" * 50 + "\n"
                
                for issue in issues_by_severity[severity]:
                    report += f"File: {issue['file']}:{issue['line']}\n"
                    report += f"Type: {issue['type']}\n"
                    report += f"Description: {issue['description']}\n"
                    report += f"Code: {issue['code']}\n"
                    report += "\n"
        
        return report
    
    def generate_json_report(self, scan_results: Dict[str, Any]) -> str:
        """Generate JSON report for CI/CD integration"""
        return json.dumps(scan_results, indent=2)

def main():
    if len(sys.argv) < 2:
        print("Usage: python security_scan.py <directory> [--json]")
        sys.exit(1)
    
    directory = sys.argv[1]
    output_json = '--json' in sys.argv
    
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist")
        sys.exit(1)
    
    scanner = SecurityScanner()
    print(f"Scanning directory: {directory}")
    
    scan_results = scanner.scan_directory(directory)
    
    if output_json:
        print(scanner.generate_json_report(scan_results))
    else:
        print(scanner.generate_report(scan_results))
    
    # Exit with error code if critical or high issues found
    critical_high_issues = sum(1 for issue in scan_results['issues'] 
                              if issue['severity'] in ['CRITICAL', 'HIGH'])
    
    if critical_high_issues > 0:
        print(f"\nFound {critical_high_issues} critical/high security issues!")
        sys.exit(1)
    else:
        print("\nNo critical security issues found!")
        sys.exit(0)

if __name__ == "__main__":
    main() 