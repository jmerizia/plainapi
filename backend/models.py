from typing import List
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
    hashed_password: str
    is_admin: bool
    joined: datetime

class UserPublic(BaseModel):
    id: RecordId
    is_admin: bool
    joined: datetime

class Field(BaseModel):
    id: RecordId
    value: str
    endpoint_id: RecordId
    location: int
    created: datetime
    updated: datetime

class Endpoint(BaseModel):
    id: RecordId
    title: str
    method: str
    location: int
    api_id: RecordId
    created: datetime
    updated: datetime

class API(BaseModel):
    id: RecordId
    title: str
    user_id: RecordId
    created: datetime
    updated: datetime
