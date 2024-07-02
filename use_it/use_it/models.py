from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: Optional[int]=None
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
