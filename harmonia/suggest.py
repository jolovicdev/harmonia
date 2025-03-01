from typing import List, Set, Dict, Optional, Tuple
import re
import string
from functools import lru_cache
from collections import defaultdict
from .dictionary import Dictionary
from .utils import soundex, levenshtein
from .config import (
    MAX_SUGGESTIONS, MAX_EDIT_DISTANCE, SUBSTITUTIONS,
    ENABLE_SUGGESTION_CACHE, SUGGESTION_CACHE_SIZE
)

@lru_cache(maxsize=SUGGESTION_CACHE_SIZE if ENABLE_SUGGESTION_CACHE else 0)
def weighted_distance(s1: str, s2: str) -> float:
    """Calculate weighted edit distance considering common typing errors."""
    base_distance = levenshtein(s1, s2, MAX_EDIT_DISTANCE)
    
    if base_distance > MAX_EDIT_DISTANCE:
        return float(base_distance)
    
    if len(s1) > 2 and len(s2) > 2:
        if s1[0] == s2[0]:
            base_distance *= 0.8
        if s1[-1] == s2[-1]:
            base_distance *= 0.9
            
    vowels = set('aeiou')
    vowel_diff = sum(1 for c1, c2 in zip(s1, s2) 
                    if c1 != c2 and c1 in vowels and c2 in vowels)
    if vowel_diff:
        base_distance *= 0.95
        
    return base_distance

def generate_edits(word: str) -> Set[str]:
    """Generate variations based on common error patterns."""
    if not word:
        return set()
        
    word = word.lower()
    variations = set()
    
    # Generate splits for edit operations
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    
    # 1. Deletions (single character removal)
    # 'wrod' -> 'word'
    for left, right in splits:
        if right:  # Can't delete from empty string
            variations.add(left + right[1:])
    
    # 2. Transpositions (swapping adjacent characters)
    # 'wrod' -> 'word'
    for left, right in splits:
        if len(right) > 1:  # Need at least 2 chars to swap
            variations.add(left + right[1] + right[0] + right[2:])
    
    # 3. Targeted substitutions (using common error patterns)
    # Much faster than substituting all possible letters
    for i, c in enumerate(word):
        if c in SUBSTITUTIONS:
            for replacement in SUBSTITUTIONS[c]:
                variations.add(word[:i] + replacement + word[i+1:])
    
    # 4. Insertions (only for short words, and with targeted letters)
    # For longer words, only consider common insertion patterns
    if len(word) <= 5:  # Only for shorter words to limit candidates
        for left, right in splits:
            for c in 'aeioust':  # Most commonly inserted letters
                variations.add(left + c + right)
    
    return variations

def generate_suggestions(word: str, dictionary: Dictionary, max_suggestions: int = MAX_SUGGESTIONS) -> List[str]:
    """Generate spelling suggestions for misspelled words."""
    if not word or len(word) < 2:
        return []
    
    original = word.lower()
    candidates: Dict[str, float] = {}
    word_len = len(original)
    
    # Generate edit variations
    edit_variations = generate_edits(original)
    
    # Check variations against dictionary
    for variation in edit_variations:
        if variation in dictionary.words:
            distance = weighted_distance(original, variation)
            if distance <= MAX_EDIT_DISTANCE:
                candidates[variation] = distance
    
    # Check similar length words
    similar_words = dictionary.get_similar_length_words(original, tolerance=1)
    
    # Process similar words in batches
    batch_size = 100
    for i in range(0, len(similar_words), batch_size):
        batch = list(similar_words)[i:i+batch_size]
        for word in batch:
            if word not in candidates:
                distance = weighted_distance(original, word)
                if distance <= MAX_EDIT_DISTANCE:
                    candidates[word] = distance
    
    # Add phonetic matches
    word_soundex = soundex(original)
    soundex_matches = {
        w for w in similar_words
        if dictionary.soundex_cache.get(w) == word_soundex
    }
    
    for word in soundex_matches:
        if word not in candidates:
            distance = weighted_distance(original, word)
            if distance <= MAX_EDIT_DISTANCE:
                candidates[word] = distance * 0.9
    
    # Sort candidates
    def suggestion_key(item):
        word, distance = item
        freq = dictionary.get_frequency(word)
        length_diff = abs(len(word) - word_len)
        return (distance, -freq, length_diff, word)
    
    sorted_candidates = sorted(candidates.items(), key=suggestion_key)
    
    return [word for word, _ in sorted_candidates[:max_suggestions]]