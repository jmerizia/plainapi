from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel


RecordId = int

class Token(BaseModel):
    access_token: str
    token_type: str
    id: RecordId

class User(BaseModel):
    id: RecordId
    email: str
    nickname: str
    score: int
    is_admin: bool
    verified: bool
    rank: Optional[int]
    created: datetime
    updated: datetime

class Endpoint(BaseModel):
    id: RecordId
    user_id: RecordId
    created: datetime
    updated: datetime

class Field(BaseModel):
    id: RecordId
    method: str
    endpoint_id: RecordId
    value: str
    created: datetime
    updated: datetime
