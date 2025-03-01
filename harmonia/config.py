"""
Configuration settings for Harmonia spell checker.
"""

import os
from typing import Dict, List, Set

# External resources
DICTIONARY_URL = (
    "https://raw.githubusercontent.com/dwyl/english-words/refs/heads/master/words.txt"
)
FREQUENCY_URL = (
    "https://raw.githubusercontent.com/IlyaSemenov/wikipedia-word-frequency/master/results/enwiki-2023-04-13.txt"
)

# File locations
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DICT_FILENAME = 'english_dictionary.txt'
FREQ_FILENAME = 'word_freq.txt'

# Algorithm parameters
MAX_SUGGESTIONS = 5
MAX_EDIT_DISTANCE = 2
SUGGESTION_CACHE_SIZE = 1000
SOUNDEX_LENGTH = 4
MIN_WORD_LENGTH = 2
SUGGESTION_BATCH_SIZE = 50

# Performance settings
ENABLE_SOUNDEX_CACHE = True
ENABLE_SUGGESTION_CACHE = True
USE_PARALLEL_PROCESSING = False  # For future implementation
DOWNLOAD_TIMEOUT = 20  # seconds

# Common letter substitutions for spell suggestions
SUBSTITUTIONS: Dict[str, str] = {
    'a': 'eiouy', 
    'e': 'aiouy', 
    'i': 'aeouy', 
    'o': 'aeiuy', 
    'u': 'aeioy',
    'y': 'aeiou', 
    'c': 'sk', 
    'k': 'c', 
    's': 'c', 
    'v': 'fw', 
    'w': 'v',
    'f': 'phv', 
    'j': 'g', 
    'g': 'j',
    'm': 'n',
    'n': 'm',
    'd': 't',
    't': 'd',
    'b': 'p',
    'p': 'b'
}

# Soundex phonetic encoding character mapping
SOUNDEX_MAPPING: Dict[str, str] = {
    'b': '1', 'f': '1', 'p': '1', 'v': '1',
    'c': '2', 'g': '2', 'j': '2', 'k': '2', 'q': '2', 's': '2', 'x': '2', 'z': '2',
    'd': '3', 't': '3',
    'l': '4',
    'm': '5', 'n': '5',
    'r': '6'
}

# HTML Report settings
HTML_STYLE = """
    body { 
        font-family: system-ui, -apple-system, sans-serif; 
        white-space: pre-wrap; 
        margin: 2em;
        line-height: 1.5;
    }
    .misspelled {
        border-bottom: 2px solid #FF3B30;
        cursor: help;
        position: relative;
        display: inline-block;
    }
    .meta {
        color: #666;
        font-size: 0.9em;
        margin-top: 2em;
    }
"""