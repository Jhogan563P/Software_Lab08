from fastapi import FastAPI
from pydantic import BaseModel

from app.services.customer_service.application.use_cases import RegisterCustomerUseCase
from app.services.customer_service.store import customer_repository
from app.shared.health import rabbit_healthcheck


class CustomerDTO(BaseModel):
    customer_id: str
    name: str
    email: str


app = FastAPI(title="Customer Service")


@app.post("/customers")
def register_customer(d: CustomerDTO):
    use_case = RegisterCustomerUseCase(customer_repository)
    customer = use_case.execute(d.customer_id, d.name, d.email)
    return {"status": "created", "customer_id": customer.customer_id}


@app.get("/health/rabbit")
def health_rabbit():
    return rabbit_healthcheck()
