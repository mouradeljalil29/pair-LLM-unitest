"""
ID: f10
Strate: medium
Complexité cyclomatique attendue: 6
Notes: règles complexes (notation soustractive), validation stricte.
"""


ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
VALID_SUBTRACTIONS = {"IV", "IX", "XL", "XC", "CD", "CM"}


def roman_to_int(s: str) -> int:
    """
    Convertit un nombre romain (chaîne) en entier.

    Plage valide : 1 à 3999.
    Lève ValueError si la chaîne n'est pas un nombre romain valide
    (caractères inconnus, soustraction interdite, chaîne vide).
    Lève TypeError si l'entrée n'est pas une chaîne.
    """
    if not isinstance(s, str):
        raise TypeError("L'entrée doit être une chaîne")
    if not s:
        raise ValueError("Chaîne vide")
    s = s.upper()

    if any(c not in ROMAN_VALUES for c in s):
        raise ValueError(f"Caractère romain invalide dans: {s}")

    total = 0
    i = 0
    while i < len(s):
        if i + 1 < len(s) and ROMAN_VALUES[s[i]] < ROMAN_VALUES[s[i + 1]]:
            pair = s[i : i + 2]
            if pair not in VALID_SUBTRACTIONS:
                raise ValueError(f"Soustraction invalide: {pair}")
            total += ROMAN_VALUES[s[i + 1]] - ROMAN_VALUES[s[i]]
            i += 2
        else:
            total += ROMAN_VALUES[s[i]]
            i += 1
    return total
