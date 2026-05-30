from dataclasses import dataclass
from datetime import datetime


@dataclass
class Notification:
    customer_id: str
    channel: str
    message: str
    sent_at: datetime | None = None
