from dataclasses import dataclass

@dataclass
class Transaction:
    """
    Represents a financial transaction.
    """
    description: str
    amount: float
    category: str 