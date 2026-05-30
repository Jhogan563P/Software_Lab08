from app.services.notifications_service.infrastructure.messaging.publisher import RabbitRewardProcessedPublisher
from app.services.rewards_service.application.use_cases import ProcessRewardUseCase
from app.services.rewards_service.infrastructure.messaging.consumer import RabbitRewardConsumer
from app.services.rewards_service.store import repo


def main() -> None:
    reward_uc = ProcessRewardUseCase(repo)
    processed_reward_publisher = RabbitRewardProcessedPublisher()
    consumer = RabbitRewardConsumer(reward_uc, processed_reward_publisher)
    consumer.start()


if __name__ == "__main__":
    main()
