# Harmonia Spell Checker

A fast, (pretty) accurate python spell checker, inspired by pyspellchecker. Features:

- Optimized dictionary loading
- Phonetic (Soundex) matching
- Hyphen/quote variation support
- Levenshtein distance-based suggestions

## CLI Usage
```bash
harmonia check file.txt -> shows errors
harmonia check file.txt --suggest -> shows errors + suggestions
```

## Python API Usage
```python
from harmonia import Dictionary, check_file

dictionary = Dictionary() #only english right now
errors = check_file("file.txt", dictionary, suggest=True)

for error in errors:
    print(f"Error: {error['word']} at line {error['line']}")
    if error['suggestions']:
        print(f"Suggestions: {', '.join(error['suggestions'])}")


Check works well!