#!/usr/bin/env python
"""Simple test runner to check if tests can at least be imported and counted."""

import sys
import os

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        # Try to import test module
        print("Importing test_payments module...")
        import test_payments
        print("SUCCESS: Module imported")
        
        # Count test functions
        import inspect
        test_count = 0
        class_count = 0
        
        for name, obj in inspect.getmembers(test_payments):
            if inspect.isclass(obj) and name.startswith('Test'):
                class_count += 1
                methods = [m for m in dir(obj) if m.startswith('test_')]
                test_count += len(methods)
                print(f"  {name}: {len(methods)} test methods")
        
        print(f"\nTotal: {test_count} tests in {class_count} classes")
        
        # Try importing pytest
        print("\nChecking pytest...")
        try:
            import pytest
            print(f"pytest version: {pytest.__version__}")
        except ImportError as e:
            print(f"pytest not available: {e}")
        
        return 0
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
