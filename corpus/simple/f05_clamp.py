"""
ID: f05
Strate: simple
Complexité cyclomatique attendue: 4
Notes: teste la capacité du LLM à couvrir les bornes (lo, hi inclus/exclus).
"""


def clamp(value, lo, hi):
    """
    Contraint `value` dans l'intervalle [lo, hi].

    Retourne lo si value < lo, hi si value > hi, sinon value.
    Lève ValueError si lo > hi.
    """
    if lo > hi:
        raise ValueError("lo doit être <= hi")
    if value < lo:
        return lo
    if value > hi:
        return hi
    return value
