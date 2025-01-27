from typing import List, Set, Tuple
import re
from .dictionary import Dictionary
from collections import defaultdict
import string

def levenshtein_distance(s1: str, s2: str) -> int:
    """Optimized iterative Levenshtein implementation with early exit"""
    if s1 == s2:
        return 0
    if len(s1) < len(s2):
        s1, s2 = s2, s1

    # Use single array storage and swap instead of full matrix
    current = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        previous = current
        current = [i + 1] + [0] * len(s2)
        for j, c2 in enumerate(s2):
            cost = 0 if c1 == c2 else 1
            current[j+1] = min(
                previous[j+1] + 1,  # deletion
                current[j] + 1,      # insertion
                previous[j] + cost   # substitution
            )
            # Early exit if distance exceeds max allowed
            if i > j + 2 and j == len(s2)-1 and current[j+1] > 2:
                return current[j+1]
    return current[-1]

from .utils import soundex

def edits1(word: str) -> Set[str]:
    """Generate single-edit variations"""
    letters = string.ascii_lowercase
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    
    operations = set()
    operations.update(L + R[1:] for L, R in splits if R)
    operations.update(L + c + R for L, R in splits for c in letters)
    operations.update(L + c + R[1:] for L, R in splits if R for c in letters)
    operations.update(L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1)
    
    return operations

def weighted_distance(s1: str, s2: str) -> float:
    """
    Calculate weighted edit distance considering common typing errors
    and character positions.
    """
    base_distance = levenshtein_distance(s1, s2)
    
    # Apply position-based weighting
    if len(s1) > 2 and len(s2) > 2:
        if s1[0] == s2[0]:  # Same first letter
            base_distance *= 0.8
        if s1[-1] == s2[-1]:  # Same last letter
            base_distance *= 0.9
            
    # Vowel substitution should cost less
    vowels = set('aeiou')
    vowel_diff = sum(1 for c1, c2 in zip(s1, s2) 
                    if c1 != c2 and c1 in vowels and c2 in vowels)
    if vowel_diff:
        base_distance *= 0.95
        
    return base_distance

def generate_suggestions(word: str, dictionary: Dictionary, max_suggestions: int = 5) -> List[str]:
    """Generate spelling suggestions using multiple algorithms"""
    original_lower = word.lower()
    candidates = {}
    
    # 1. Generate edit distance variations
    edit_variations = set()
    # Deletions
    edit_variations.update(original_lower[:i] + original_lower[i+1:]
                         for i in range(len(original_lower)))
    # Transpositions
    edit_variations.update(original_lower[:i] + original_lower[i+1] + original_lower[i] + original_lower[i+2:]
                         for i in range(len(original_lower)-1))
    # Replacements (focusing on common substitutions)
    substitutions = {
        'a': 'eiouy', 'e': 'aiouy', 'i': 'aeouy', 'o': 'aeiuy', 'u': 'aeioy',
        'y': 'aeiou', 'c': 'sk', 'k': 'c', 's': 'c', 'v': 'fw', 'w': 'v',
        'f': 'phv', 'j': 'g', 'g': 'j'
    }
    for i, c in enumerate(original_lower):
        if c in substitutions:
            edit_variations.update(
                original_lower[:i] + r + original_lower[i+1:]
                for r in substitutions[c]
            )
    
    # 2. Check variations against dictionary
    word_len = len(original_lower)
    for variation in edit_variations:
        if variation in dictionary.words:
            distance = levenshtein_distance(original_lower, variation)
            if distance <= 2:  # Only consider close matches
                candidates[variation] = distance
    
    # 3. Check similar length words with same first letter
    similar_words = dictionary.get_similar_length_words(original_lower, tolerance=1)
    filtered_words = {
        w for w in similar_words 
        if w[0] == original_lower[0]
        and abs(len(w) - word_len) <= 1
    }
    
    for dict_word in filtered_words:
        if dict_word not in candidates:  # Avoid rechecking
            distance = levenshtein_distance(original_lower, dict_word)
            if distance <= 2:
                candidates[dict_word] = distance
    
    # 4. Add phonetic matches
    soundex_matches = {
        w for w in filtered_words
        if dictionary.soundex_cache.get(w) == soundex(original_lower)
    }
    for word in soundex_matches:
        if word not in candidates:
            distance = levenshtein_distance(original_lower, word)
            if distance <= 2:
                candidates[word] = distance
    
    # Sort by edit distance and frequency
    sorted_candidates = sorted(
        candidates.items(),
        key=lambda x: (x[1], -dictionary.get_frequency(x[0]), x[0])
    )
    
    return [word for word, _ in sorted_candidates[:max_suggestions]]