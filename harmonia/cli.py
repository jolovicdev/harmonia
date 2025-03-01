#!/usr/bin/env python3
"""
CLI module for the Harmonia Spell Checker.
"""

import os
import argparse
import sys
import logging
import time
from typing import Set, List, Dict, Optional
from .dictionary import Dictionary
from .checker import check_file
from .formatters import generate_html_report, generate_markdown_report
from .config import MAX_SUGGESTIONS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

def read_ignore_file(filepath: str) -> Set[str]:
    """Read a file containing words to ignore during spell checking."""
    ignore_words = set()
    
    if not os.path.exists(filepath):
        logger.warning(f"Ignore file not found: {filepath}")
        return ignore_words
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip().lower()
                if word and not word.startswith('#'):
                    ignore_words.add(word)
        logger.info(f"Loaded {len(ignore_words)} words to ignore")
    except Exception as e:
        logger.error(f"Error reading ignore file: {e}")
        
    return ignore_words

def main():
    """CLI entrypoint for Harmonia spell checker."""
    parser = argparse.ArgumentParser(
        description='Harmonia - A fast and accurate Python spell checker',
        epilog='Example: harmonia check myfile.txt --suggest --html report.html'
    )
    parser.add_argument('--version', action='store_true', help='Show version information')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')

    subparsers = parser.add_subparsers(dest='command')

    # Check command
    check_parser = subparsers.add_parser('check', help='Check spelling in a file')
    check_parser.add_argument('filepath', help='Path to the file to check')
    check_parser.add_argument('--suggest', '-s', action='store_true', 
                             help='Show suggestions for each error')
    check_parser.add_argument('--html', metavar='OUTPUT_FILE',
                             help='Generate HTML report')
    check_parser.add_argument('--markdown', metavar='OUTPUT_FILE',
                             help='Generate Markdown report')
    check_parser.add_argument('--ignore', '-i', metavar='IGNORE_FILE',
                             help='File containing words to ignore (one per line)')
    check_parser.add_argument('--max-suggestions', type=int, default=MAX_SUGGESTIONS,
                             help=f'Maximum number of suggestions per word (default: {MAX_SUGGESTIONS})')
    check_parser.add_argument('--quiet', '-q', action='store_true',
                             help='Suppress console output')

    args = parser.parse_args()
    
    # Show version and exit
    if args.version:
        print("Harmonia Spell Checker v1.2.0")
        return

    # Require command
    if not args.command:
        parser.print_help()
        return

    # Set verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        if args.command == 'check':
            # Measure performance
            start_time = time.time()
            
            # Initialize dictionary
            dictionary = Dictionary(verbose=args.verbose)
            
            # Load ignore words if specified
            ignore_words = set()
            if args.ignore:
                ignore_words = read_ignore_file(args.ignore)
            
            # Check the file
            results = check_file(
                args.filepath, 
                dictionary, 
                suggest=args.suggest or args.html or args.markdown,
                ignore_words=ignore_words
            )
            
            # Read original text for reports
            text = ""
            try:
                with open(args.filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
            except UnicodeDecodeError:
                # Try alternative encodings
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        with open(args.filepath, 'r', encoding=encoding) as f:
                            text = f.read()
                        break
                    except:
                        continue

            # Generate HTML report if requested
            if args.html:
                title = f"Spell Check: {os.path.basename(args.filepath)}"
                html_output = generate_html_report(text, results, title=title)
                with open(args.html, 'w', encoding='utf-8') as f:
                    f.write(html_output)
                if not args.quiet:
                    print(f"HTML report written to: {args.html}")

            # Generate Markdown report if requested
            if args.markdown:
                md_output = generate_markdown_report(text, results)
                with open(args.markdown, 'w', encoding='utf-8') as f:
                    f.write(md_output)
                if not args.quiet:
                    print(f"Markdown report written to: {args.markdown}")

            # Calculate elapsed time
            elapsed = time.time() - start_time
            
            # Print console output unless quiet mode is enabled
            if not args.quiet:
                if results:
                    print(f"Found {len(results)} errors in {args.filepath}")
                    print(f"Completed in {elapsed:.2f} seconds")
                    
                    for error in results:
                        loc = f"Line {error['line']}, Position {error['position']}"
                        print(f"\n{loc} - {error['word']}")
                        if error['suggestions']:
                            max_to_show = min(args.max_suggestions, 5)  # Show at most 5 in console
                            print("  Suggestions:", ", ".join(error['suggestions'][:max_to_show]))
                else:
                    print(f"No spelling errors found in {args.filepath}")
                    print(f"Completed in {elapsed:.2f} seconds")

    except KeyboardInterrupt:
        sys.exit("\nInterrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    # Allow running via `python -m harmonia.cli check somefile.txt --suggest`
    main()
