from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DinnerRegisteredEvent:
    amount: float
    card_number: str
    restaurant_id: str
    timestamp: datetime


@dataclass(frozen=True)
class RewardProcessedEvent:
    customer_id: str
    points: int
    cashback: float
    processed_at: datetime
