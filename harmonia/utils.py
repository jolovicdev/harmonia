from typing import Dict, Optional
from functools import lru_cache
from .config import SOUNDEX_MAPPING, SOUNDEX_LENGTH

# Pre-compile the mapping for faster lookups
_SOUNDEX_MAP = SOUNDEX_MAPPING

@lru_cache(maxsize=10000)
def soundex(word: str) -> str:
    """Optimized Soundex algorithm for phonetic matching."""
    if not word:
        return ""
    
    word = word.lower()
    first_char = word[0].upper()
    
    result = [first_char]
    last_code = None
    
    for char in word[1:]:
        code = _SOUNDEX_MAP.get(char, '0')
        
        if code != '0' and code != last_code:
            result.append(code)
            last_code = code
            
            if len(result) >= SOUNDEX_LENGTH:
                break
    
    result_str = ''.join(result)
    return (result_str + '0000')[:SOUNDEX_LENGTH]

def levenshtein(s1: str, s2: str, max_dist: Optional[int] = None) -> int:
    """Fast Levenshtein distance implementation with early termination."""
    # Ensure s1 is the shorter string for performance
    if len(s1) > len(s2):
        s1, s2 = s2, s1
        
    # Fast paths
    if s1 == s2:
        return 0
    
    len1, len2 = len(s1), len(s2)
    
    # If max_dist is provided, use it for early termination
    if max_dist is not None:
        # If the length difference is already too big, we can return early
        if abs(len1 - len2) > max_dist:
            return max_dist + 1
    
    # Single-row approach to minimize memory usage
    current = list(range(len2 + 1))
    
    for i in range(len1):
        previous, current = current, [i + 1] + [0] * len2
        
        for j in range(len2):
            add, delete, change = previous[j + 1] + 1, current[j] + 1, previous[j]
            if s1[i] != s2[j]:
                change += 1
            current[j + 1] = min(add, delete, change)
        
        # Early termination check
        if max_dist is not None and min(current) > max_dist:
            return max_dist + 1
            
    return current[len2]