"""
ID: f03
Strate: simple
Complexité cyclomatique attendue: 3
Notes: fonction custom (anti-contamination), règles métier spécifiques France.
"""


def validate_french_postal_code(code: str) -> bool:
    """
    Valide un code postal français.

    Règles :
    - exactement 5 chiffres
    - les deux premiers chiffres représentent un département valide
      (01 à 95, plus 97 et 98 pour DOM-TOM, hors 96)
    - "00000" est invalide
    """
    if not isinstance(code, str):
        return False
    if len(code) != 5 or not code.isdigit():
        return False
    if code == "00000":
        return False
    dept = int(code[:2])
    valid_depts = set(range(1, 96)) | {97, 98}
    return dept in valid_depts
