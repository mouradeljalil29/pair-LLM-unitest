"""
ID: f11
Strate: complex
Complexité cyclomatique attendue: 8 (cumulée sur les méthodes)
Notes: classe avec état interne, plusieurs méthodes, gestion d'erreurs.
"""


class BankAccount:
    """
    Compte bancaire simplifié avec deposit, withdraw et transfer.

    - Le solde initial doit être >= 0
    - Les montants doivent être strictement positifs
    - withdraw lève InsufficientFundsError si solde insuffisant
    - transfer fait un withdraw puis un deposit sur l'autre compte
    """

    def __init__(self, owner: str, balance: float = 0.0):
        if not isinstance(owner, str) or not owner:
            raise ValueError("Propriétaire invalide")
        if balance < 0:
            raise ValueError("Solde initial négatif interdit")
        self.owner = owner
        self.balance = float(balance)
        self.history = []

    def deposit(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Le montant doit être strictement positif")
        self.balance += amount
        self.history.append(("deposit", amount))
        return self.balance

    def withdraw(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Le montant doit être strictement positif")
        if amount > self.balance:
            raise InsufficientFundsError(
                f"Solde insuffisant: {self.balance} < {amount}"
            )
        self.balance -= amount
        self.history.append(("withdraw", amount))
        return self.balance

    def transfer(self, other: "BankAccount", amount: float) -> None:
        if not isinstance(other, BankAccount):
            raise TypeError("Destinataire doit être un BankAccount")
        if other is self:
            raise ValueError("Transfert vers soi-même interdit")
        self.withdraw(amount)
        other.deposit(amount)


class InsufficientFundsError(Exception):
    """Levée quand un retrait dépasse le solde disponible."""

    pass
