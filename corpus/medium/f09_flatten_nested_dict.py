"""
ID: f09
Strate: medium
Complexité cyclomatique attendue: 5
Notes: récursion + collision de clés.
"""


def flatten_nested_dict(d: dict, sep: str = ".") -> dict:
    """
    Aplatit un dictionnaire imbriqué.

    Exemple : {"a": {"b": 1, "c": 2}, "d": 3} -> {"a.b": 1, "a.c": 2, "d": 3}

    - Les listes sont conservées telles quelles (pas d'aplatissement).
    - Si une collision de clés se produit après aplatissement, la dernière
      valeur écrase la précédente.
    - Lève TypeError si l'entrée n'est pas un dict.
    """
    if not isinstance(d, dict):
        raise TypeError("L'entrée doit être un dict")

    def _flatten(obj, parent_key):
        items = {}
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else str(k)
            if isinstance(v, dict):
                items.update(_flatten(v, new_key))
            else:
                items[new_key] = v
        return items

    return _flatten(d, "")
