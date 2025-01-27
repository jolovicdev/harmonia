#!/usr/bin/env python3
"""
CLI module for the Harmonia Spell Checker.
"""

import argparse
import sys
from .dictionary import Dictionary
from .checker import check_file
from .formatters import generate_html_report

def main():
    parser = argparse.ArgumentParser(description='Harmonia Spell Checker')
    subparsers = parser.add_subparsers(dest='command', required=True)

    check_parser = subparsers.add_parser('check', help='Check spelling in a file.')
    check_parser.add_argument('filepath', help='Path to the file to check')
    check_parser.add_argument('--suggest', action='store_true', help='Show suggestions for each error')
    check_parser.add_argument('--html', help='Generate HTML report', metavar='OUTPUT_FILE')

    args = parser.parse_args()

    try:
        dictionary = Dictionary()
        results = check_file(args.filepath, dictionary, suggest=args.suggest)

        # Generate HTML report if requested
        if args.html:
            with open(args.filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            html_output = generate_html_report(text, results)
            with open(args.html, 'w', encoding='utf-8') as f:
                f.write(html_output)
            print(f"\nHTML report written to: {args.html}")

        # Print console output
        print(f"Found {len(results)} errors")
        for error in results:
            loc = f"Line {error['line']}, Position {error['position']}"
            print(f"\n{loc} - {error['word']}")
            if error['suggestions']:
                print("  Suggestions:", ", ".join(error['suggestions'][:3]))

    except KeyboardInterrupt:
        sys.exit("\nInterrupted by user")

if __name__ == '__main__':
    # Allow running via `python -m harmonia.cli check somefile.txt --suggest`
    main()
