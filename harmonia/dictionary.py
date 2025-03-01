"""
Dictionary management: loading known words, frequencies, and common misspellings.
"""

import os
import re
import time
import logging
import requests
from typing import Set, Dict, Optional, Tuple
from collections import defaultdict
from functools import lru_cache
from .utils import soundex
from .config import (
    DICTIONARY_URL, FREQUENCY_URL,
    DATA_DIR, DICT_FILENAME, FREQ_FILENAME,
    DOWNLOAD_TIMEOUT, ENABLE_SOUNDEX_CACHE
)

# Configure logging
logger = logging.getLogger(__name__)

class Dictionary:
    """Dictionary for spell checking with word frequencies and misspellings."""

    def __init__(self, verbose: bool = False):
        self.words: Set[str] = set()
        self.frequency: Dict[str, int] = defaultdict(int)
        self.soundex_cache: Dict[str, str] = {}
        self.word_lengths: Dict[int, Set[str]] = defaultdict(set)
        self.verbose = verbose
        
        # Set up paths
        self.data_dir = DATA_DIR
        self.dict_path = os.path.join(self.data_dir, DICT_FILENAME)
        self.freq_path = os.path.join(self.data_dir, FREQ_FILENAME)
        
        # Timestamp for caching
        self.last_loaded = 0
        
        # Ensure data directory exists
        self._ensure_data_files()
        
        # Load dictionary data
        self.load()

    def _ensure_data_files(self):
        """Create data directory if missing."""
        os.makedirs(self.data_dir, exist_ok=True)

    def load(self):
        """
        Load dictionary words and frequencies from local files.
        If files are missing, download them from the specified URLs.
        """
        self.last_loaded = time.time()
        
        if self.verbose:
            logger.info("Starting dictionary load...")
        
        # Load data files
        self._ensure_dictionary_file()
        self._ensure_frequency_file()
        
        try:
            # Load dictionary words
            self._load_dictionary_words()
            
            # Load word frequencies
            self._load_word_frequencies()
            
            # Add derived word forms
            self._add_derived_forms()
            
        except KeyboardInterrupt:
            logger.warning("Dictionary loading interrupted by user")
    
    def _ensure_dictionary_file(self):
        """Download dictionary file if not found."""
        if not os.path.exists(self.dict_path):
            if self.verbose:
                logger.info("Downloading dictionary...")
            try:
                self._download(DICTIONARY_URL, self.dict_path)
            except Exception as e:
                logger.error(f"Failed to download dictionary: {e}")
                raise
    
    def _ensure_frequency_file(self):
        """Download frequency file if not found."""
        if not os.path.exists(self.freq_path):
            if self.verbose:
                logger.info("Downloading word frequency data...")
            try:
                self._download(FREQUENCY_URL, self.freq_path)
            except Exception as e:
                logger.warning(f"Failed to download frequency data: {e}")
                # Create empty file to prevent repeated download attempts
                with open(self.freq_path, 'w', encoding='utf-8') as f:
                    pass
    
    # Common misspellings are now directly defined in __init__
    
    def _load_dictionary_words(self):
        """Load dictionary words from file."""
        if not os.path.exists(self.dict_path):
            logger.warning("Dictionary file not found")
            return
            
        if self.verbose:
            logger.info("Loading dictionary words...")
            
        valid_words = set()
        word_count = 0
        
        with open(self.dict_path, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip().lower()
                # Accept words with letters and apostrophes
                if re.match(r"^[a-z']+$", word):
                    valid_words.add(word)
                    word_count += 1
                    
                    # Only log progress in verbose mode
                    if self.verbose and word_count % 50000 == 0:
                        logger.info(f"Loaded {word_count} words...")
                    
                    # Precompute data during initial load
                    if ENABLE_SOUNDEX_CACHE:
                        self.soundex_cache[word] = soundex(word)
                    self.word_lengths[len(word)].add(word)
        
        self.words.update(valid_words)
        
        if self.verbose:
            logger.info(f"Total words loaded: {word_count}")
    
    def _load_word_frequencies(self):
        """Load word frequencies from file."""
        if not os.path.exists(self.freq_path) or os.path.getsize(self.freq_path) == 0:
            return
            
        try:
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
        except Exception as e:
            logger.warning(f"Failed to load frequency data: {e}")
    
    # Misspellings are now defined directly in __init__
    
    def _add_derived_forms(self):
        """Add common derived word forms to the dictionary."""
        # Add basic word forms that might be missing
        original_words = list(self.words)
        derived_forms = set()
        
        for word in original_words:
            # Add common plural forms
            if word.endswith('y'):
                derived_forms.add(word[:-1] + 'ies')
            elif not word.endswith('s'):
                derived_forms.add(word + 's')
                
            # Add common past tense forms
            if word.endswith('e'):
                derived_forms.add(word + 'd')
            else:
                derived_forms.add(word + 'ed')
                
            # Add common -ing forms
            if word.endswith('e'):
                derived_forms.add(word[:-1] + 'ing')
            else:
                derived_forms.add(word + 'ing')
        
        # Update the main word set
        self.words.update(derived_forms)
        
        # Add derived words to the length index
        for word in derived_forms:
            self.word_lengths[len(word)].add(word)
            
        if self.verbose:
            logger.info(f"Added {len(derived_forms)} derived word forms")

    def _download(self, url: str, dest: str):
        """Robust download with basic error handling."""
        try:
            response = requests.get(url, timeout=DOWNLOAD_TIMEOUT)
            response.raise_for_status()
            with open(dest, 'w', encoding='utf-8') as f:
                f.write(response.text)
        except Exception as e:
            raise RuntimeError(f"Failed to download {url}: {e}")

    def __contains__(self, word: str) -> bool:
        """Optimized dictionary lookup."""
        if not word or len(word) < 2:
            return False
        
        lower_word = word.lower()
        
        if lower_word in self.words:
            return True
            
        if "'" in lower_word:
            if lower_word.endswith("'s"):
                return lower_word[:-2] in self.words
            
            parts = lower_word.split("'")
            if len(parts) == 2:
                common_contractions = {
                    "dont": "do not", "cant": "cannot", "wont": "will not",
                    "isnt": "is not", "arent": "are not", "wasnt": "was not",
                    "werent": "were not", "hasnt": "has not", "havent": "have not",
                    "hadnt": "had not", "didnt": "did not", "wouldnt": "would not",
                    "shouldnt": "should not", "couldnt": "could not",
                    "im": "i am", "youre": "you are", "hes": "he is",
                    "shes": "she is", "its": "it is", "were": "we are",
                    "theyre": "they are"
                }
                contraction = ''.join(parts)
                if contraction in common_contractions:
                    return True
            
        if '-' in lower_word:
            parts = [part for part in lower_word.split('-') if part]
            if all(part in self.words for part in parts):
                return True
                
        return False

    @lru_cache(maxsize=1000)
    def get_frequency(self, word: str) -> int:
        """Get word frequency from dictionary."""
        return self.frequency.get(word.lower(), 0)

    def get_similar_length_words(self, word: str, tolerance: int = 1) -> Set[str]:
        """Find words of similar length for spell checking."""
        word_len = len(word)
        first_char = word[0].lower() if word else ''
        
        candidates = set()
        
        for length in range(max(1, word_len - tolerance), 
                           min(word_len + tolerance + 1, max(self.word_lengths.keys()) + 1)):
            words_of_length = self.word_lengths.get(length, set())
            
            candidates.update(w for w in words_of_length if w.startswith(first_char))
            
            if len(candidates) < 100:
                other_candidates = [w for w in words_of_length if not w.startswith(first_char)]
                sample_size = min(100, len(other_candidates) // 10) 
                candidates.update(other_candidates[:sample_size])
        
        return candidates
        
    def refresh(self) -> bool:
        """Refresh dictionary data for long-running applications."""
        if time.time() - self.last_loaded > 86400:  # 24 hours
            self.load()
            return True
        return False
