from pydantic import BaseModel


class ExchangeLoginRequest(BaseModel):
    code: str
