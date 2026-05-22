"""
ID: f06
Strate: medium
Complexité cyclomatique attendue: 5
Notes: plusieurs formats acceptés, gestion d'exceptions.
"""

from datetime import datetime


def parse_iso_date(s: str) -> datetime:
    """
    Parse une date au format ISO 8601 (avec ou sans heure).

    Formats acceptés :
    - "YYYY-MM-DD"
    - "YYYY-MM-DDTHH:MM:SS"
    - "YYYY-MM-DDTHH:MM:SSZ" (UTC)

    Lève ValueError si le format est invalide ou la date impossible.
    Lève TypeError si l'entrée n'est pas une chaîne.
    """
    if not isinstance(s, str):
        raise TypeError("L'entrée doit être une chaîne")
    if not s:
        raise ValueError("Chaîne vide")
    candidate = s.rstrip("Z")
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(candidate, fmt)
        except ValueError:
            continue
    raise ValueError(f"Format de date invalide: {s}")
