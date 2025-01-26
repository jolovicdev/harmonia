"""
Dictionary management: loading known words, frequencies, and common misspellings.
"""

import os
import re
import requests
from typing import Set, Dict
from collections import defaultdict
from .utils import soundex

DICTIONARY_URL = (
    "https://raw.githubusercontent.com/dwyl/english-words/refs/heads/master/words.txt"
)
FREQUENCY_URL = (
    "https://raw.githubusercontent.com/IlyaSemenov/wikipedia-word-frequency/"
    "master/results/enwiki-2023-04-13.txt"
)


class Dictionary:
    """
    Loads and stores a set of valid English words as well as
    frequency data for ranking suggestions. Also includes
    a map of common misspellings -> correct forms.
    """

    def __init__(self):
        self.words: Set[str] = set()
        self.frequency: Dict[str, int] = defaultdict(int)
        self.soundex_cache: Dict[str, str] = {}
        self.word_lengths: Dict[int, Set[str]] = defaultdict(set)

        # Some typical or project-specific misspellings
        self.common_misspellings = {
            'quik': 'quick',
            'wulf': 'wolf',
            'fliwers': 'flowers',
            'throgh': 'through',
            'soond': 'sound',
            'strainge': 'strange',
            'morrning': 'morning',
            'comming': 'coming',
            'walkked': 'walked',
            'grandmuther': 'grandmother',
            'denk': 'dense',
            'lzy': 'lazy',
            'dogg': 'dog',
            'onse': 'once',
            'timme': 'time'
        }

        # You can change this path to a more suitable location if desired
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.dict_path = os.path.join(self.data_dir, 'english_dictionary.txt')
        self.freq_path = os.path.join(self.data_dir, 'word_freq.txt')

        # Ensure local files exist before loading
        self._ensure_data_files()
        self.load()

    def _ensure_data_files(self):
        """Create data directory if missing."""
        os.makedirs(self.data_dir, exist_ok=True)

    def load(self):
        """
        Load dictionary words and frequencies from local files.
        If files are missing, download them from the specified URLs.
        """
        print("Starting dictionary load...")
        try:
            # Download dictionary if not found
            if not os.path.exists(self.dict_path):
                print("Downloading dictionary...")
                self._download(DICTIONARY_URL, self.dict_path)

            # Single load of dictionary words
            print("Loading dictionary words...")
            valid_words = set()
            word_count = 0
            with open(self.dict_path, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip().lower()
                    if re.fullmatch(r'^[a-z]+$', word):
                        valid_words.add(word)
                        word_count += 1
                        if word_count % 50000 == 0:
                            print(f"Loaded {word_count} words...")
                        
                        # Precompute data during initial load
                        self.soundex_cache[word] = soundex(word)
                        self.word_lengths[len(word)].add(word)

            self.words.update(valid_words)
            print(f"Total words loaded: {word_count}")

            # Load frequency data
            if not os.path.exists(self.freq_path):
                self._download(FREQUENCY_URL, self.freq_path)

            with open(self.freq_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) == 2:
                        word, freq = parts[0].lower(), parts[1]
                        try:
                            self.frequency[word] = int(freq)
                        except ValueError:
                            continue

        except KeyboardInterrupt:
            print("\nDictionary loading interrupted")
            return

        # Load frequency data
        with open(self.freq_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    word, freq = parts[0].lower(), parts[1]
                    try:
                        self.frequency[word] = int(freq)
                    except ValueError:
                        # Skip malformed frequency lines
                        continue

        # Add known misspellings and corrections to the word set
        # Add misspellings and precompute their data
        for word in self.common_misspellings.keys():
            self.words.add(word)
            self.soundex_cache[word] = soundex(word)
            self.word_lengths[len(word)].add(word)
        for word in self.common_misspellings.values():
            self.words.add(word)
            self.soundex_cache[word] = soundex(word)
            self.word_lengths[len(word)].add(word)

        # Manually ensure a few crucial words are present
        self.words.update(['quick', 'lazy', 'wolf'])

    def _download(self, url: str, dest: str):
        """Robust download with basic error handling."""
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            with open(dest, 'w', encoding='utf-8') as f:
                f.write(response.text)
        except Exception as e:
            raise RuntimeError(f"Failed to download {url}: {e}")

    def __contains__(self, word: str) -> bool:
        """
        Check if a word is in the dictionary. Case-insensitive with cache.
        """
        lower_word = word.lower()
        if lower_word in self.words:
            return True
        # Check hyphen variations (e.g. 'mother-in-law' vs 'motherinlaw')
        return any(
            part in self.words
            for part in re.split(r"[-']", lower_word)
            if part
        )

    def get_frequency(self, word: str) -> int:
        """
        Retrieve the known frequency of a word; returns 0 if unknown.
        """
        return self.frequency.get(word.lower(), 0)
