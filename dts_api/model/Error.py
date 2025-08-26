from pydantic import BaseModel


class BaseErrorMessage(BaseModel):
    error: "ErrorDict"

class ErrorDict(BaseModel):
    code: int
    type: str
    message: str
    details: list[dict] | str | None