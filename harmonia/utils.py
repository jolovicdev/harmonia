from typing import Dict

def soundex(word: str) -> str:
    """Soundex algorithm for phonetic matching"""
    if not word:
        return ""
    
    first_char = word[0].upper()
    word = word.lower()
    
    mapping = {
        'b': '1', 'f': '1', 'p': '1', 'v': '1',
        'c': '2', 'g': '2', 'j': '2', 'k': '2', 'q': '2', 's': '2', 'x': '2', 'z': '2',
        'd': '3', 't': '3',
        'l': '4',
        'm': '5', 'n': '5',
        'r': '6'
    }
    
    result = [first_char]
    for char in word[1:]:
        code = mapping.get(char, '0')
        if code != '0' and code != result[-1]:
            result.append(code)
    
    result = ''.join(result)
    return (result + '000')[:4]