"""Simple test runner for LCARS project.
Finds tests in the `tests/` directory and runs them, printing results to stdout.
Designed to be callable from UI or subprocess.
"""
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
import argparse
import unittest
from io import StringIO


def run_tests(pattern='test_*.py'):
    # Ensure project root is on sys.path so tests can import `lcars`
    project_root = os.getcwd()
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='tests', pattern=pattern)
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    output = stream.getvalue()
    summary = f"\nRan {result.testsRun} tests. Failures: {len(result.failures)}; Errors: {len(result.errors)}\n"
    return output + summary

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pattern', '-p', default='test_*.py', help='unittest discovery pattern (default: test_*.py)')
    args = parser.parse_args()
    out = run_tests(pattern=args.pattern)
    sys.stdout.write(out)
    sys.exit(0 if ("FAIL" not in out and "ERROR" not in out) else 1)
