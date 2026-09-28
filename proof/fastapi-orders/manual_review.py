from pydantic import BaseModel, validator


class LegacyOrder(BaseModel):
    quantity: int

    @validator("quantity")
    def dependent_validation(cls, value, values):
        return value
