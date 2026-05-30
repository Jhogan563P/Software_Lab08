import pytest
from fastapi.testclient import TestClient

from app.services.rewards_service.api import app as rewards_app
from app.services.rewards_service.store import repo as rewards_repo
from app.services.customer_service.store import customer_repository
from app.services.rewards_service.application.use_cases import ProcessRewardUseCase
from app.services.notifications_service.infrastructure.delivery.in_memory import InMemoryNotificationSender
from app.services.notifications_service.application.use_cases import NotifyRewardProcessedUseCase

pytestmark = pytest.mark.integration


def test_reward_creates_customer_and_sends_notification():
    # reset in-memory stores
    rewards_repo._items.clear()
    customer_repository._items.clear()

    payload = {"card_number": "1111222233334444", "amount": 120.0}

    reward_uc = ProcessRewardUseCase(rewards_repo)
    account = reward_uc.execute(payload)

    # account created and updated
    assert account.customer_id == "4444"
    assert account.points == 12

    # customer should have been created
    customer = customer_repository.get("4444")
    assert customer is not None

    # send notification using in-memory sender
    sender = InMemoryNotificationSender()
    notify_uc = NotifyRewardProcessedUseCase(sender)
    notify_uc.execute(account.customer_id, account.points, account.cashback)

    assert len(sender.sent) == 1
    assert str(account.points) in sender.sent[0].message

    # API returns the account data
    client = TestClient(rewards_app)
    r = client.get(f"/accounts/{account.customer_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["points"] == account.points
    assert float(data["cashback"]) == float(account.cashback)
