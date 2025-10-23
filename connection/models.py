from typing import Optional

from pydantic import BaseModel


class DiskUser(BaseModel):
    login: str
    display_name: str


class DiskInfoResponse(BaseModel):
    user: DiskUser


class ErrorResponse(BaseModel):
    error: str
    description: str
    message: Optional[str] = None
