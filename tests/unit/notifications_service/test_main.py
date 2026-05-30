"""
Unit tests for NotificationsService entry point.
Marker: unit
"""
import pytest

import app.services.notifications_service.main as notifications_main

pytestmark = pytest.mark.unit


def test_notifications_main_creates_consumer_and_starts(monkeypatch):
    instances = []

    class FakeConsumer:
        def __init__(self, notification_use_case):
            self.notification_use_case = notification_use_case
            self.started = False
            instances.append(self)

        def start(self):
            self.started = True

    monkeypatch.setattr(notifications_main, "RabbitNotificationConsumer", FakeConsumer)

    notifications_main.main()

    assert len(instances) == 1
    assert instances[0].started is True
    assert instances[0].notification_use_case is not None