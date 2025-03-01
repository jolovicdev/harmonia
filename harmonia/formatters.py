"""
Output formatters for spell checking results.
"""

import html
import time
from typing import List, Dict, Optional, Union
from datetime import datetime
from .config import HTML_STYLE

def generate_html_report(
    text: str, 
    errors: List[Dict], 
    title: str = "Spelling Check Results",
    include_stats: bool = True
) -> str:
    """Generate HTML report with highlighted spelling errors and hover suggestions."""
    # Escape HTML special characters
    html_text = html.escape(text)
    lines = html_text.split('\n')
    
    # Sort errors in reverse order to maintain positions
    sorted_errors = sorted(errors, key=lambda x: (x['line'], x['position']), reverse=True)
    
    # Add underlining and tooltips for each error
    for error in sorted_errors:
        line_idx = error['line'] - 1
        if line_idx >= len(lines):
            continue  # Skip if line number is out of bounds
            
        pos = error['position'] - 1
        word = error['word']
        suggestions = error['suggestions']
        
        # Create tooltip with suggestions
        if suggestions:
            suggestion_text = ', '.join(suggestions)
            tooltip = f"Suggestions: {html.escape(suggestion_text)}"
        else:
            tooltip = "No suggestions available"
            
        # Create highlighted word with tooltip
        marked_word = (
            f'<span class="misspelled" title="{tooltip}">'
            f'{html.escape(word)}</span>'
        )
        
        # Replace the misspelled word in the line
        if 0 <= pos < len(lines[line_idx]):
            line = lines[line_idx]
            # Make sure we're actually replacing the right word
            if pos + len(word) <= len(line):
                lines[line_idx] = line[:pos] + marked_word + line[pos + len(word):]
    
    # Generate statistics if requested
    stats_html = ""
    if include_stats and errors:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        word_count = len(text.split())
        error_count = len(errors)
        error_rate = (error_count / word_count) * 100 if word_count > 0 else 0
        
        stats_html = f"""
<div class="meta">
    <p>Spell check completed on {current_time}</p>
    <p>Found {error_count} errors in {word_count} words ({error_rate:.2f}% error rate)</p>
    <p>Generated with <a href="https://github.com/jolovicdev/harmonia">Harmonia Spell Checker</a> v1.2.0</p>
</div>
"""
    
    # Construct the full HTML document
    template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <style>
    {HTML_STYLE}
    </style>
</head>
<body>
{'\n'.join(lines)}
{stats_html}
</body>
</html>"""
    
    return template

def generate_markdown_report(text: str, errors: List[Dict]) -> str:
    """Generate a markdown report with spelling errors."""
    lines = text.split('\n')
    result = ["# Spelling Check Results\n"]
    
    # Group errors by line
    for error in sorted(errors, key=lambda x: (x['line'], x['position'])):
        line_idx = error['line'] - 1
        if line_idx >= len(lines):
            continue
            
        line_text = lines[line_idx].strip()
        word = error['word']
        suggestions = error['suggestions']
        
        result.append(f"## Line {error['line']}, Position {error['position']}\n")
        result.append(f"> {line_text}\n")
        result.append(f"**Error**: '{word}'\n")
        
        if suggestions:
            result.append(f"**Suggestions**: {', '.join(suggestions)}\n")
        else:
            result.append("No suggestions available\n")
    
    # Add summary
    result.append(f"\n## Summary\n")
    result.append(f"Total errors found: {len(errors)}\n")
    result.append(f"Generated with Harmonia Spell Checker v1.2.0\n")
    
    return '\n'.join(result)