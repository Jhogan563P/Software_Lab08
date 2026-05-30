from datetime import UTC, datetime
from fastapi import FastAPI
from pydantic import BaseModel, Field
from app.customer.application.use_cases import RegisterCustomerUseCase
from app.customer.infrastructure.repository.in_memory import InMemoryCustomerRepository
from app.dinner.application.use_cases import RegisterDinnerUseCase
from app.dinner.domain.entities import DinnerTransaction
from app.dinner.infrastructure.messaging.rabbit_publisher import RabbitDinnerPublisher
from app.shared.config.settings import AppSettings


class DinnerDTO(BaseModel):
    amount: float = Field(..., gt=0)
    card_number: str = Field(..., min_length=12)
    restaurant_id: str
    timestamp: datetime = None


class CustomerDTO(BaseModel):
    customer_id: str
    name: str
    email: str


def create_publisher():
    return RabbitDinnerPublisher(AppSettings())


customer_repository = InMemoryCustomerRepository()


app = FastAPI(title="Rewards Producer API")


@app.post("/customers")
def register_customer(d: CustomerDTO):
    use_case = RegisterCustomerUseCase(customer_repository)
    customer = use_case.execute(d.customer_id, d.name, d.email)
    return {"status": "created", "customer_id": customer.customer_id}


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
