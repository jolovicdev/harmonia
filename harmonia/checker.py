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
    Improved regex to better catch misspelled words.
    """
    # First split on whitespace to preserve word positions
    words = []
    for word in line.split():
        # Clean the word but preserve apostrophes and hyphens
        clean_word = re.sub(r'[^a-zA-Z\'-]', '', word)
        if clean_word:
            words.append(clean_word)
    return words


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
                start_pos = 0
                
                for word in words:
                    # Find actual position in line
                    pos = line.find(word, start_pos)
                    if pos == -1:
                        continue
                    start_pos = pos + len(word)

                    # Skip numbers and very short words
                    if len(word) < 2 or word.isdigit():
                        continue
                        
                    # Skip words that are all punctuation
                    if not any(c.isalpha() for c in word):
                        continue

                    # Check if word is valid
                    if not dictionary.__contains__(word):
                        error_entry = {
                            'word': word,
                            'line': line_num,
                            'position': pos + 1,
                            'suggestions': []
                        }
                        if suggest:
                            error_entry['suggestions'] = generate_suggestions(word, dictionary)
                        results.append(error_entry)

    except UnicodeDecodeError:
        print(f"Warning: Unable to decode file {filepath}, skipping.")
        return []

    return results