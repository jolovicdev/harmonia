#!/usr/bin/env python3
"""
CLI module for the Harmonia Spell Checker.
"""

import argparse
import sys

from .dictionary import Dictionary
from .checker import check_file


def main():
    parser = argparse.ArgumentParser(description='Harmonia Spell Checker')
    subparsers = parser.add_subparsers(dest='command', required=True)

    check_parser = subparsers.add_parser('check', help='Check spelling in a file.')
    check_parser.add_argument('filepath', help='Path to the file to check')
    check_parser.add_argument('--suggest', action='store_true', help='Show suggestions for each error')

    args = parser.parse_args()

    dictionary = Dictionary()
    results = check_file(args.filepath, dictionary, suggest=args.suggest)

    print(f"Found {len(results)} errors")
    for error in results:
        loc = f"Line {error['line']}, Position {error['position']}"
        print(f"\n{loc} - {error['word']}")
        if error['suggestions']:
            print("  Suggestions:", ", ".join(error['suggestions'][:3]))


if __name__ == '__main__':
    # Allow running via `python -m harmonia.cli check somefile.txt --suggest`
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("Interrupted by user")
