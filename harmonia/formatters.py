"""
Output formatters for spell checking results.
"""

from typing import List, Dict
import html

def generate_html_report(text: str, errors: List[Dict]) -> str:
    """Convert text and spelling errors into HTML with hover suggestions."""
    html_text = html.escape(text)
    lines = html_text.split('\n')
    
    # Sort errors in reverse order to maintain positions
    sorted_errors = sorted(errors, key=lambda x: (x['line'], x['position']), reverse=True)
    
    # Add underlining and tooltips for each error
    for error in sorted_errors:
        line_idx = error['line'] - 1
        pos = error['position'] - 1
        word = error['word']
        suggestions = error['suggestions']
        
        tooltip = f"Suggestions: {', '.join(suggestions)}" if suggestions else "No suggestions"
        marked_word = (
            '<span style="border-bottom: 2px solid red; cursor: help" '
            f'title="{html.escape(tooltip)}">{html.escape(word)}</span>'
        )
        
        line = lines[line_idx]
        lines[line_idx] = line[:pos] + marked_word + line[pos + len(word):]
    
    template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Spell Check Results</title>
    <style>
        body { font-family: monospace; white-space: pre-wrap; margin: 2em; }
    </style>
</head>
<body>
{content}
</body>
</html>"""
    
    return template.format(content='\n'.join(lines)) 