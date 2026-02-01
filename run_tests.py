#!/usr/bin/env python
"""
Test Runner - Executes payment tests and generates report
Workaround for Python 3.14 / SQLAlchemy compatibility issue
"""

import sys
import os
import subprocess

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    """Execute payment test suite."""
    print("\n" + "="*80)
    print("PAYMENT TEST SUITE EXECUTION")
    print("="*80)
    print(f"Python Version: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    print("="*80 + "\n")
    
    # Run pytest with proper parameters
    cmd = [
        sys.executable, 
        '-m', 'pytest', 
        'test_payments.py',
        '-v',
        '--tb=short',
        '--co',  # Collect tests only first
    ]
    
    print(f"Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
    
    return result.returncode

if __name__ == '__main__':
    sys.exit(run_tests())
