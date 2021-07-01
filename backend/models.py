from typing import List, Union, Literal
from enum import Enum
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

class Endpoint(BaseModel):
    # id: RecordId
    # api_id: RecordId
    method: str
    url: str
    value: str
    # sql_query: str

# class Migration(BaseModel):
#     id: RecordId
#     api_id: RecordId
#     value: str
#     applied: bool
#     sql_query: str

class API(BaseModel):
    id: RecordId
    title: str
    endpoints: List[Endpoint]
    # migrations: List[Migration]
    user_id: RecordId
    created: datetime
    updated: datetime
