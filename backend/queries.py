import sqlite3
from typing import List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
import json

from models import RecordId, User, API, Endpoint
from utils import expect_env


load_dotenv()
DATABASE_URL = expect_env("DATABASE_URL")

con = sqlite3.connect(DATABASE_URL.split(':')[-1])
cur = con.cursor()


def insert_user(email: str, hashed_password: str, is_admin: bool, joined: datetime) -> User:
    id = cur.execute('''
        INSERT INTO users (email, hashed_password, is_admin, joined) VALUES (?, ?, ?, ?);
    ''', (email, hashed_password, is_admin, joined.isoformat())).lastrowid
    con.commit()
    user = select_user_by_id(id=id)
    if user is None:
        raise ValueError('Internal Error as occurred')
    return user

def select_user_by_id(id: int) -> Optional[User]:
    cols = ['id', 'email', 'hashed_password', 'is_admin', 'joined']
    row = cur.execute(f'''
        SELECT {', '.join(cols)} FROM users WHERE id = ?;
    ''', (id, )).fetchone()
    if row is None:
        return None
    d: Any = dict()
    for k, v in zip(cols, row):
        d[k] = v
    return User(
        id=d['id'],
        email=d['email'],
        hashed_password=d['hashed_password'],
        is_admin=d['is_admin'],
        joined=datetime.fromisoformat(d['joined'])
    )

def select_user_by_email(email: str) -> Optional[User]:
    cols = ['id', 'email', 'hashed_password', 'is_admin', 'joined']
    row = cur.execute(f'''
        SELECT {', '.join(cols)} FROM users WHERE email = ?;
    ''', (email, )).fetchone()
    if row is None:
        return None
    d: Any = dict()
    for k, v in zip(cols, row):
        d[k] = v
    return User(
        id=d['id'],
        email=d['email'],
        hashed_password=d['hashed_password'],
        is_admin=d['is_admin'],
        joined=datetime.fromisoformat(d['joined'])
    )

def select_all_users() -> List[User]:
    cols = ['id', 'email', 'hashed_password', 'is_admin', 'joined']
    rows = cur.execute(f'''
        SELECT {', '.join(cols)} FROM users;
    ''').fetchall()
    users: List[User] = []
    for row in rows:
        d: Any = dict()
        for k, v in zip(cols, row):
            d[k] = v
        user = User(
            id=d['id'],
            email=d['email'],
            hashed_password=d['hashed_password'],
            is_admin=d['is_admin'],
            joined=datetime.fromisoformat(d['joined'])
        )
        users.append(user)
    return users

def update_user(id: int, email: Optional[str] = None, is_admin: Optional[bool] = None) -> None:
    if email is not None:
        cur.execute('''
            UPDATE users SET email = ? WHERE id = ?;
        ''', (email, id, ))
    if is_admin is not None:
        cur.execute('''
            UPDATE users SET is_admin = ? WHERE id = ?;
        ''', (is_admin, id, ))
    con.commit()

def delete_user(id: int) -> None:
    cur.execute('''
        DELETE FROM users WHERE id = ?;
    ''', (id, ))
    con.commit()

def insert_api(title: str, serialized_endpoints: str, user_id: RecordId, created: datetime, updated: datetime) -> API:
    id = cur.execute('''
        INSERT INTO apis (title, endpoints, user_id, created, updated) VALUES (?, ?, ?, ?, ?);
    ''', (title, serialized_endpoints, user_id, created.isoformat(), updated.isoformat())).lastrowid
    con.commit()
    api = select_api_by_id(id=id)
    if api is None:
        raise ValueError('Unexpected API is null')
    return api

def select_api_by_id(id: RecordId) -> Optional[API]:
    cols = ['id', 'title', 'endpoints', 'user_id', 'created', 'updated']
    row = cur.execute(f'''
        SELECT {', '.join(cols)} FROM apis WHERE id = ?;
    ''', (id, )).fetchone()
    if row is None:
        return None
    d: Any = dict()
    for k, v in zip(cols, row):
        d[k] = v
    return API(
        id=d['id'],
        title=d['title'],
        endpoints=json.loads(d['endpoints']),
        user_id=d['user_id'],
        created=datetime.fromisoformat(d['created']),
        updated=datetime.fromisoformat(d['updated'])
    )

def select_apis_for_user(user_id: RecordId) -> List[API]:
    cols = ['id', 'title', 'endpoints', 'user_id', 'created', 'updated']
    rows = cur.execute(f'''
        SELECT {', '.join(cols)} FROM apis WHERE user_id = ?;
    ''', (user_id, )).fetchall()
    apis: List[API] = []
    for row in rows:
        d: Any = dict()
        for k, v in zip(cols, row):
            d[k] = v
        api = API(
            id=d['id'],
            title=d['title'],
            endpoints=json.loads(d['endpoints']),
            user_id=d['user_id'],
            created=datetime.fromisoformat(d['created']),
            updated=datetime.fromisoformat(d['updated'])
        )
        apis.append(api)
    return apis

def update_api(id: RecordId, title: Optional[str] = None, serialized_endpoints: Optional[str] = None, user_id: Optional[RecordId] = None, created: Optional[datetime] = None, updated: Optional[datetime] = None) -> None:
    if title is not None:
        cur.execute('''
            UPDATE apis SET title = ? WHERE id = ?;
        ''', (title, id, ))
    if serialized_endpoints is not None:
        cur.execute('''
            UPDATE apis SET endpoints = ? WHERE id = ?;
        ''', (serialized_endpoints, id, ))
    if user_id is not None:
        cur.execute('''
            UPDATE apis SET user_id = ? WHERE id = ?;
        ''', (user_id, id, ))
    if created is not None:
        cur.execute('''
            UPDATE apis SET created = ? WHERE id = ?;
        ''', (created.isoformat(), id, ))
    if updated is not None:
        cur.execute('''
            UPDATE apis SET updated = ? WHERE id = ?;
        ''', (updated.isoformat(), id, ))
    con.commit()

def delete_api(id: RecordId) -> None:
    cur.execute('''
        DELETE FROM apis WHERE id = ?;
    ''', (id, ))
    con.commit()
