"""
ID: f08
Strate: medium
Complexité cyclomatique attendue: 7
Notes: règles métier custom (anti-contamination), beaucoup de branches.
"""


def calculate_discount(price: float, customer_type: str, quantity: int) -> float:
    """
    Calcule le prix final après application des remises.

    Règles :
    - customer_type doit être "standard", "premium" ou "vip"
    - "premium" : -5%
    - "vip" : -10%
    - quantity >= 10 : -5% supplémentaire (cumulable)
    - quantity >= 50 : -10% supplémentaire (remplace la remise quantité ci-dessus)
    - prix négatif ou quantité <= 0 lève ValueError
    - customer_type invalide lève ValueError
    """
    if price < 0:
        raise ValueError("Le prix ne peut pas être négatif")
    if quantity <= 0:
        raise ValueError("La quantité doit être strictement positive")
    if customer_type not in ("standard", "premium", "vip"):
        raise ValueError(f"Type de client inconnu: {customer_type}")

    discount = 0.0
    if customer_type == "premium":
        discount += 0.05
    elif customer_type == "vip":
        discount += 0.10

    if quantity >= 50:
        discount += 0.10
    elif quantity >= 10:
        discount += 0.05

    return price * quantity * (1 - discount)
