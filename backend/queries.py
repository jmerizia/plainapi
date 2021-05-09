import sqlite3

from models import RecordId, StringWrapper, Token, User, Endpoint, Field
from utils import expect_env


def create_user(email: str, hashed_password: str) -> User:
    pass

def select_user_by_id(id: int) -> User:
    pass

def select_user_by_email(email: str) -> User:
    pass

def update_user() -> None:
    pass

def delete_user() -> None:
    pass
