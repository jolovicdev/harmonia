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

def generate_suggestions(word: str, dictionary: Dictionary, max_edits: int = 2) -> List[str]:
    """Optimized suggestion generator with candidate prioritization"""
    original_lower = word.lower()
    candidates = defaultdict(int)
    
    # 1. Check common misspellings first
    if correction := dictionary.common_misspellings.get(original_lower):
        candidates[correction] += dictionary.get_frequency(correction) * 2
    
    # 2. Check Soundex matches using precomputed cache
    soundex_code = soundex(original_lower)
    for dict_word, s_code in dictionary.soundex_cache.items():
        if s_code == soundex_code:
            candidates[dict_word] += dictionary.get_frequency(dict_word)
    
    # 3. Generate single-edit candidates
    for edit in edits1(original_lower):
        if edit in dictionary:
            candidates[edit] += dictionary.get_frequency(edit)
    
    # 4. Limited double-edit candidates for common error patterns
    if max_edits >= 2 and len(original_lower) > 3:
        common_edits = (original_lower[:i] + c + original_lower[i+1:]
                       for i in range(len(original_lower))
                       for c in 'aeiou')
        for edit in common_edits:
            if edit in dictionary:
                candidates[edit] += dictionary.get_frequency(edit)
    
    # 5. Remove original word if present
    candidates.pop(original_lower, None)
    
    # Sort by frequency then alphabetical order
    sorted_words = sorted(
        candidates.items(),
        key=lambda x: (-x[1], x[0]),
    )
    
    return [word for word, _ in sorted_words[:5]]