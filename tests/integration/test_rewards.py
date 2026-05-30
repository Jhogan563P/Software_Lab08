import pytest
from app.services.rewards_service.application.use_cases import ProcessRewardUseCase
from app.services.rewards_service.infrastructure.repository.in_memory import InMemoryRewardRepository

pytestmark = pytest.mark.integration


def test_calculate_points_and_cashback():
    repo = InMemoryRewardRepository()
    uc = ProcessRewardUseCase(repo)

    points, cashback = uc.calculate(250.0)

    assert points == 25
    assert cashback == 2.5


def test_execute_updates_repository():
    repo = InMemoryRewardRepository()
    uc = ProcessRewardUseCase(repo)

    payload = {"amount": 120.0, "card_number": "1234567890123456"}
    result = uc.execute(payload)

    stored = repo.get(result.customer_id)
    assert stored is not None
    assert stored.points == 12
    assert round(stored.cashback, 2) == 1.2
