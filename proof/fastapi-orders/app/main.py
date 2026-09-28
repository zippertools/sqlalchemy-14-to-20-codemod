from app.models import Order
from app.settings import Settings
from fastapi import FastAPI

app = FastAPI()


@app.post("/orders", response_model=Order)
def create_order(order: Order):
    return order


@app.get("/health")
def health():
    return {"service": Settings().service_name}
