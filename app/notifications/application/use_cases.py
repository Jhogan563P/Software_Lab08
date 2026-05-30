from datetime import UTC, datetime
from app.notifications.domain.entities import Notification
from app.notifications.domain.ports import NotificationSender


class NotifyRewardProcessedUseCase:
    def __init__(self, sender: NotificationSender):
        self.sender = sender

    def execute(self, customer_id: str, points: int, cashback: float) -> Notification:
        notification = Notification(
            customer_id=customer_id,
            channel="email",
            message=f"Tu recompensa fue procesada: {points} puntos y {cashback} de cashback.",
            sent_at=datetime.now(UTC),
        )
        self.sender.send(notification)
        return notification
