from app.services.dinner_service.domain.entities import DinnerTransaction
from app.services.dinner_service.domain.ports import DinnerPublisher


class RegisterDinnerUseCase:
    def __init__(self, publisher: DinnerPublisher):
        self.publisher = publisher

    def execute(self, dinner: DinnerTransaction) -> DinnerTransaction:
        self.publisher.publish_dinner(dinner)
        return dinner
