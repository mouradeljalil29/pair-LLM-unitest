"""
Fonction de référence pour la génération de tests LLM.

ID: f01
Strate: simple
Complexité cyclomatique attendue: 2
Notes: fonction classique, probablement vue par les LLM en entraînement (contamination possible).
"""


def is_palindrome(s: str) -> bool:
    """
    Renvoie True si la chaîne `s` est un palindrome.

    Les caractères non-alphanumériques sont ignorés et la casse n'est pas
    prise en compte. Une chaîne vide est considérée comme palindrome.
    """
    if not isinstance(s, str):
        raise TypeError("L'argument doit être une chaîne de caractères")
    cleaned = "".join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]
