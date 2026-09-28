from pydantic import BaseModel, validator


class Order(BaseModel):
    customer: str
    quantity: int

    @validator("customer")
    def normalize_customer(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("customer required")
        return value

    @validator("quantity")
    def positive_quantity(cls, value):
        if value < 1:
            raise ValueError("quantity must be positive")
        return value

    class Config:
        extra = "forbid"
