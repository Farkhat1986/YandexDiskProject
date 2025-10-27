from pydantic import BaseModel


class DiskUser(BaseModel):
    login: str
    display_name: str


class DiskInfoResponse(BaseModel):
    user: DiskUser


class ErrorResponse(BaseModel):
    error: str | None = None
    description: str | None = None
    message: str | None = None
