"""
Spell-check logic: reading files, tokenizing lines, and collecting errors.
"""

import re
from typing import List, Dict

from .suggest import generate_suggestions
from .dictionary import Dictionary


def tokenize(line: str) -> List[str]:
    """
    Tokenize a line, capturing words with apostrophes and hyphens.
    Optimized regex with lookbehind/lookahead assertions.
    """
    return re.findall(r"(?i)(?<!\S)[a-z]+(?:['’-][a-z]+)*(?!\S)", line)


def check_file(filepath: str, dictionary: Dictionary, suggest: bool = False) -> List[Dict]:
    """
    Read a file line by line, tokenizing words and checking each one
    against the given dictionary. If 'suggest' is True, generate suggestions.
    Return a list of error dictionaries.
    """
    results = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                words = tokenize(line)
                for pos, word in enumerate(words, 1):
                    if not re.match(r"^[a-zA-Z']+$", word):
                        continue

                    lower_word = word.lower()
                    if lower_word not in dictionary:
                        error_entry = {
                            'word': word,
                            'line': line_num,
                            'position': pos,
                            'suggestions': []
                        }
                        if suggest:
                            error_entry['suggestions'] = generate_suggestions(word, dictionary)
                        results.append(error_entry)

    except UnicodeDecodeError: 
        print(f"Warning: Unable to decode file {filepath}, skipping.")
        pass

    return results