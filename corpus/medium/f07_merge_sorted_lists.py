"""
ID: f07
Strate: medium
Complexité cyclomatique attendue: 5
Notes: algorithmique classique, plusieurs edge cases (vide, doublons).
"""


def merge_sorted_lists(a: list, b: list) -> list:
    """
    Fusionne deux listes triées en une seule liste triée.

    Préserve les doublons (stable). Lève TypeError si l'une des listes
    contient des éléments non comparables.
    """
    if not isinstance(a, list) or not isinstance(b, list):
        raise TypeError("Les deux arguments doivent être des listes")

    result = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1
    result.extend(a[i:])
    result.extend(b[j:])
    return result
