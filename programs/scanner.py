"""Unified scanner CLI for LCARS Framework.

Usage examples:
  python programs/scanner.py --list
  python programs/scanner.py --scan odn
"""
import argparse
import json
from programs.scanner import ScannerEngine


def main():
    p = argparse.ArgumentParser(description="LCARS unified scanner CLI")
    p.add_argument("--list", action="store_true", help="List available scanners")
    p.add_argument("--scan", metavar="NAME", help="Run a named scanner")
    p.add_argument("--json", action="store_true", help="Output JSON (when printing results)")
    args = p.parse_args()

    eng = ScannerEngine()

    if args.list:
        for n in eng.list_scanners():
            print(n)
        return

    if args.scan:
        try:
            res = eng.scan(args.scan)
            if args.json:
                print(json.dumps(res, indent=2, default=str))
            else:
                print(res)
        except Exception as e:
            print("Scan error:", e)
        return

    p.print_help()


if __name__ == "__main__":
    main()
