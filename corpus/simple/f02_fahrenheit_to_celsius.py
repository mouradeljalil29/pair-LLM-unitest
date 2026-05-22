"""
ID: f02
Strate: simple
Complexité cyclomatique attendue: 2
Notes: edge cases physiques (zéro absolu), valeurs limites.
"""


def fahrenheit_to_celsius(f: float) -> float:
    """
    Convertit une température en Fahrenheit vers Celsius.

    Lève ValueError si la température est en-dessous du zéro absolu
    (-459.67 °F).
    """
    if not isinstance(f, (int, float)) or isinstance(f, bool):
        raise TypeError("La température doit être un nombre")
    if f < -459.67:
        raise ValueError("Température en-dessous du zéro absolu")
    return (f - 32) * 5.0 / 9.0
