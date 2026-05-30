from app.notifications.domain.entities import Notification
from app.notifications.domain.ports import NotificationSender


class InMemoryNotificationSender(NotificationSender):
    def __init__(self):
        self.sent: list[Notification] = []

    def send(self, notification: Notification) -> None:
        self.sent.append(notification)
