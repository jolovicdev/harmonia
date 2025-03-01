"""
Spell-check logic: reading files, tokenizing lines, and collecting errors.
"""

import re
import os
import logging
from typing import List, Dict, Set, Optional, Union, Tuple
from .suggest import generate_suggestions
from .dictionary import Dictionary
from .config import MIN_WORD_LENGTH

# Configure logging
logger = logging.getLogger(__name__)

# Precompile the regex pattern for better performance
# This pattern captures words with letters, digits, apostrophes, and hyphens
_WORD_REGEX = re.compile(r'[a-zA-Z][\w\'-]*', re.UNICODE)

def tokenize(line: str) -> List[Tuple[str, int]]:
    """Tokenize a line, capturing words with apostrophes and hyphens."""
    if not line:
        return []
        
    return [(match.group(), match.start()) for match in _WORD_REGEX.finditer(line)]

def should_check_word(word: str) -> bool:
    """Determine if a word should be spell-checked."""
    # Skip if too short
    if not word or len(word) < MIN_WORD_LENGTH:
        return False
        
    # Skip numbers
    if word.isdigit():
        return False
        
    # Skip words that are all punctuation
    if not any(c.isalpha() for c in word):
        return False
        
    # Skip words that look like codes or file names (camelCase, snake_case, etc.)
    if '_' in word or word != word.lower() and word != word.upper() and word != word.title():
        return False
    
    # Skip emails and URLs
    if '@' in word or word.startswith('http') or '://' in word:
        return False
        
    return True

def check_file(
    filepath: str, 
    dictionary: Dictionary, 
    suggest: bool = False,
    ignore_words: Optional[Set[str]] = None
) -> List[Dict]:
    """Check spelling in a file and return a list of errors."""
    results = []
    ignore_words = ignore_words or set()
    
    # Check if file exists
    if not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")
        return []
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Tokenize the line
                tokens = tokenize(line)
                
                for word, pos in tokens:
                    # Skip certain words
                    if not should_check_word(word):
                        continue
                        
                    # Skip ignored words
                    if word.lower() in ignore_words:
                        continue

                    # Check if word is valid (using the proper containment method)
                    if word not in dictionary:
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
        logger.warning(f"Unable to decode file {filepath}, trying alternative encodings")
        # Try some alternative encodings
        for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    # Process with the working encoding
                    for line_num, line in enumerate(f, 1):
                        tokens = tokenize(line)
                        for word, pos in tokens:
                            if not should_check_word(word) or word.lower() in ignore_words:
                                continue
                            if word not in dictionary:
                                error_entry = {
                                    'word': word,
                                    'line': line_num,
                                    'position': pos + 1,
                                    'suggestions': []
                                }
                                if suggest:
                                    error_entry['suggestions'] = generate_suggestions(word, dictionary)
                                results.append(error_entry)
                return results
            except:
                continue
                
        logger.error(f"Failed to decode file {filepath} with all attempted encodings")
        return []
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {e}")
        return []

    return results