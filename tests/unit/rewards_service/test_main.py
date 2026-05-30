import pytest

import app.services.rewards_service.main as rewards_main

pytestmark = pytest.mark.unit


def test_rewards_main_creates_consumer_and_starts(monkeypatch):
    instances = []

    class FakeConsumer:
        def __init__(self, reward_uc, processed_reward_publisher):
            self.reward_uc = reward_uc
            self.processed_reward_publisher = processed_reward_publisher
            self.started = False
            instances.append(self)

        def start(self):
            self.started = True

    monkeypatch.setattr(rewards_main, "RabbitRewardConsumer", FakeConsumer)

    rewards_main.main()

    assert len(instances) == 1
    assert instances[0].started is True
    assert instances[0].reward_uc is not None
    assert instances[0].processed_reward_publisher is not None