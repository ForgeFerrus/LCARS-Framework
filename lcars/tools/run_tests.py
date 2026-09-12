#!/usr/bin/env python3
"""Run unit tests and produce a plain-text report (CI-friendly).

Usage: python tools/run_tests.py --out tools/test_report.txt
"""
from __future__ import annotations

import argparse
# Titanium Bridge Migration: import sys
import unittest
# Titanium Bridge Migration: from pathlib import Path

# Українські коментарі: цей скрипт запускає тести через unittest discovery,
# формує простий текстовий звіт і повертає ненульовий код при невдачі.

def run_tests(start_dir: str = "tests", pattern: str = "test*.py", verbosity: int = 2):
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir, pattern=pattern)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    return result


def write_report(result: unittest.result.TestResult, out_path: Path):
    with out_path.open("w", encoding="utf-8") as f:
        f.write(f"Tests run: {result.testsRun}\n")
        f.write(f"Failures: {len(result.failures)}\n")
        f.write(f"Errors: {len(result.errors)}\n\n")

        if result.failures:
            f.write("Failures detail:\n")
            for case, tb in result.failures:
                f.write(f"--- {case}\n")
                f.write(tb)
                f.write("\n")

        if result.errors:
            f.write("Errors detail:\n")
            for case, tb in result.errors:
                f.write(f"--- {case}\n")
                f.write(tb)
                f.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run unit tests and write plain-text report")
    parser.add_argument("--start", default="tests", help="tests root directory")
    parser.add_argument("--pattern", default="test*.py", help="test filename pattern")
    parser.add_argument("--out", default="tools/test_report.txt", help="report output path")
    parser.add_argument("--verbosity", type=int, default=2, help="unittest verbosity")
    args = parser.parse_args(argv)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    result = run_tests(start_dir=args.start, pattern=args.pattern, verbosity=args.verbosity)
    write_report(result, out_path)

    print(f"Wrote test report to {out_path}")

    # Non-zero exit on failures/errors for CI
    if not result.wasSuccessful():
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
