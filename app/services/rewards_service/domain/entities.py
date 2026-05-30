from dataclasses import dataclass
from datetime import datetime


@dataclass
class RewardAccount:
    customer_id: str
    points: int = 0
    cashback: float = 0.0
    updated_at: datetime | None = None
