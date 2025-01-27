# Harmonia Spell Checker

A fast, (pretty) accurate Python spell checker, inspired by pyspellchecker.

## Installation
```bash
pip install harmoniapy
```

## Features
- Optimized dictionary loading
- Phonetic (Soundex) matching
- Hyphen/quote variation support
- Levenshtein distance-based suggestions
- HTML report generation with hover suggestions

## CLI Usage
```bash
# Show errors
harmonia check file.txt

# Show errors with suggestions
harmonia check file.txt --suggest

# Generate HTML report with hover suggestions
harmonia check file.txt --suggest --html report.html
```

## Python API Usage
```python
from harmonia import Dictionary, check_file

# Initialize dictionary (English only for now)
dictionary = Dictionary()

# Check file with suggestions
errors = check_file("file.txt", dictionary, suggest=True)

# Process errors
for error in errors:
    print(f"Error: {error['word']} at line {error['line']}")
    if error['suggestions']:
        print(f"Suggestions: {', '.join(error['suggestions'])}")

# Generate HTML report
from harmonia.formatters import generate_html_report
with open("file.txt") as f:
    text = f.read()
html_report = generate_html_report(text, errors)
with open("report.html", "w") as f:
    f.write(html_report)
```

## HTML Report
The HTML report shows the text with red underlines for misspelled words. Hover over any underlined word to see spelling suggestions.