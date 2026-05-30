from abc import ABC, abstractmethod

from app.services.notifications_service.domain.entities import Notification


class NotificationSender(ABC):
    @abstractmethod
    def send(self, notification: Notification) -> None:
        raise NotImplementedError()
