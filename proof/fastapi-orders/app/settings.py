from pydantic import BaseSettings


class Settings(BaseSettings):
    service_name: str = "Order API"

    class Config:
        env_prefix = "ZIPPER_PROOF_"
