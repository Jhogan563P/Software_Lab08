from fastapi import FastAPI, HTTPException

from app.services.rewards_service.store import repo


app = FastAPI(title="Rewards API")


@app.get("/accounts/{customer_id}", responses={404: {"description": "Account not found"}})
def get_account(customer_id: str):
    account = repo.get(customer_id)
    if account is None:
        raise HTTPException(status_code=404, detail="account not found")
    return {"customer_id": account.customer_id, "points": account.points, "cashback": account.cashback}
