from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DinnerTransaction:
    amount: float
    card_number: str
    restaurant_id: str
    timestamp: datetime
