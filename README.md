# Harmonia Spell Checker

![Version](https://img.shields.io/badge/version-1.2.0-blue.svg) 
![Python](https://img.shields.io/badge/python-3.8%2B-green.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

A **fast**, **accurate**, and **feature-rich** Python spell checker - a powerful alternative to pyspellchecker with advanced features and optimized performance.

## 🚀 Features

- **High Performance**: Optimized dictionary loading and word lookup algorithms
- **Accurate Suggestions**: Advanced algorithms for spelling suggestions:
  - Levenshtein distance with optimized implementation
  - Phonetic matching with Soundex algorithm
  - Context-aware weighted suggestions
- **Flexible Word Handling**:
  - Support for hyphenated words
  - Contractions and possessives detection
  - Automatically derived word forms
- **Robust Output Options**:
  - Interactive command-line interface
  - Detailed HTML reports with hover suggestions
  - Markdown report generation
  - Customizable output formats
- **Developer-Friendly**:
  - Clean, well-documented API
  - Highly customizable settings
  - Comprehensive error handling
  - Memory-efficient implementation

## 📦 Installation

```bash
pip install harmoniapy
```

## 🖥️ CLI Usage

Check a file for spelling errors:

```bash
# Basic usage
harmonia check myfile.txt

# Show suggestions for each error
harmonia check myfile.txt --suggest

# Generate HTML report with hover suggestions
harmonia check myfile.txt --suggest --html report.html

# Generate Markdown report
harmonia check myfile.txt --suggest --markdown report.md

# Ignore specific words
harmonia check myfile.txt --ignore ignored-words.txt

# Show version information
harmonia --version
```

## 💻 Python API Usage

```python
from harmonia import Dictionary, check_file

# Initialize dictionary (loads automatically)
dictionary = Dictionary()

# Check file with suggestions
errors = check_file("myfile.txt", dictionary, suggest=True)

# Process errors
for error in errors:
    print(f"Error: {error['word']} at line {error['line']}")
    if error['suggestions']:
        print(f"Suggestions: {', '.join(error['suggestions'])}")

# Generate HTML report
from harmonia.formatters import generate_html_report
with open("myfile.txt") as f:
    text = f.read()
html_report = generate_html_report(text, errors)
with open("report.html", "w") as f:
    f.write(html_report)
```

## 📊 HTML Report

The HTML report shows the text with red underlines for misspelled words. Hover over any underlined word to see spelling suggestions.

## 🔄 Comparison with pyspellchecker

| Feature | Harmonia | pyspellchecker |
|---------|----------|---------------|
| Suggestion algorithm | Multi-algorithm hybrid | Primarily edit distance |
| Phonetic matching | ✅ Soundex | ❌ Not included |
| Word frequency | ✅ Wikipedia-based | ✅ Basic frequency |
| HTML reports | ✅ Interactive | ❌ Not included |
| Misspellings DB | ✅ Extensive | ✅ Limited |
| Performance | ✅ Highly optimized | ⚠️ Standard |
| Custom dictionaries | ✅ Supported | ✅ Supported |
| Hyphenated words | ✅ Advanced handling | ⚠️ Basic support |
| Derived word forms | ✅ Automatic | ❌ Not included |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.