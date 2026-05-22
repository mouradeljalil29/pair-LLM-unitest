"""
ID: f04
Strate: simple
Complexité cyclomatique attendue: 3
Notes: piège classique = les accents français. Un LLM naïf ne testera que [aeiou].
"""


VOWELS_FR = set("aeiouyàâäéèêëîïôöùûüÿ")


def count_vowels(s: str) -> int:
    """
    Compte le nombre de voyelles dans la chaîne `s`.

    Les voyelles incluent : a, e, i, o, u, y et leurs versions accentuées
    courantes en français (à, â, ä, é, è, ê, ë, î, ï, ô, ö, ù, û, ü, ÿ).
    La comparaison est insensible à la casse.
    """
    if not isinstance(s, str):
        raise TypeError("L'argument doit être une chaîne")
    return sum(1 for c in s.lower() if c in VOWELS_FR)
