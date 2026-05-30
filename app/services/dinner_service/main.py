from datetime import UTC, datetime

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.services.dinner_service.application.use_cases import RegisterDinnerUseCase
from app.services.dinner_service.domain.entities import DinnerTransaction
from app.services.dinner_service.infrastructure.messaging.rabbit_publisher import RabbitDinnerPublisher
from app.shared.config.settings import AppSettings
from app.shared.health import rabbit_healthcheck


from typing import Optional

class DinnerDTO(BaseModel):
    amount: float = Field(..., gt=0)
    card_number: str = Field(..., min_length=12)
    restaurant_id: str
    timestamp: Optional[datetime] = None


def create_publisher() -> RabbitDinnerPublisher:
    return RabbitDinnerPublisher(AppSettings())


app = FastAPI(title="Dinner Service")


@app.post("/dinner")
def register_dinner(d: DinnerDTO):
    publisher = create_publisher()
    use_case = RegisterDinnerUseCase(publisher)
    tx = d
    if tx.timestamp is None:
        tx.timestamp = datetime.now(UTC)

    domain_tx = DinnerTransaction(
        amount=tx.amount,
        card_number=tx.card_number,
        restaurant_id=tx.restaurant_id,
        timestamp=tx.timestamp,
    )
    use_case.execute(domain_tx)
    return {"status": "published", "queue": "laboratorio_1"}


@app.get("/health/rabbit")
def health_rabbit():
    return rabbit_healthcheck()
