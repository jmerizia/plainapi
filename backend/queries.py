import sqlite3
from typing import List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
import json

from models import RecordId, User, API, Endpoint, Field
from utils import expect_env


load_dotenv()
DATABASE_URL = expect_env("DATABASE_URL")

con = sqlite3.connect(DATABASE_URL.split(':')[-1])
cur = con.cursor()


# USER

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


# API

def insert_api(title: str, user_id: RecordId, created: datetime, updated: datetime) -> API:
    id = cur.execute('''
        INSERT INTO apis (title, user_id, created, updated) VALUES (?, ?, ?, ?);
    ''', (title, user_id, created.isoformat(), updated.isoformat())).lastrowid
    con.commit()
    api = select_api_by_id(id=id)
    if api is None:
        raise ValueError('Unexpected API is null')
    return api

def select_api_by_id(id: RecordId) -> Optional[API]:
    cols = ['id', 'title', 'user_id', 'created', 'updated']
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
        user_id=d['user_id'],
        created=datetime.fromisoformat(d['created']),
        updated=datetime.fromisoformat(d['updated'])
    )

def select_apis_for_user(user_id: RecordId) -> List[API]:
    cols = ['id', 'title', 'user_id', 'created', 'updated']
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
            user_id=d['user_id'],
            created=datetime.fromisoformat(d['created']),
            updated=datetime.fromisoformat(d['updated'])
        )
        apis.append(api)
    return apis

def update_api(id: RecordId, title: Optional[str] = None, user_id: Optional[RecordId] = None, created: Optional[datetime] = None, updated: Optional[datetime] = None) -> None:
    if title is not None:
        cur.execute('''
            UPDATE apis SET title = ? WHERE id = ?;
        ''', (title, id, ))
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


# ENDPOINT

def insert_endpoint(title: str, api_id: RecordId, location: int, method: str, created: datetime, updated: datetime) -> Endpoint:
    id = cur.execute('''
        INSERT INTO endpoints (title, location, method, api_id, created, updated) VALUES (?, ?, ?, ?, ?, ?);
    ''', (title, location, method, api_id, created, updated, )).lastrowid
    con.commit()
    endpoint = select_endpoint_by_id(id=id)
    if endpoint is None:
        raise ValueError('Expected endpoint to exist')
    return endpoint

def select_endpoint_by_id(id: RecordId) -> Optional[Endpoint]:
    cols = ['id', 'title', 'location', 'method', 'api_id', 'created', 'updated']
    row = cur.execute(f'''
        SELECT {', '.join(cols)} FROM endpoints WHERE id = ?;
    ''', (id, )).fetchone()
    if row is None:
        return None
    d: Any = dict()
    for k, v in zip(cols, row):
        d[k] = v
    return Endpoint(
        id=d['id'],
        title=d['title'],
        location=d['location'],
        method=d['method'],
        api_id=d['api_id'],
        created=datetime.fromisoformat(d['created']),
        updated=datetime.fromisoformat(d['updated']),
    )

def select_endpoints_for_api(api_id: RecordId) -> List[Endpoint]:
    cols = ['id', 'title', 'location', 'method', 'api_id', 'created', 'updated']
    rows = cur.execute(f'''
        SELECT {', '.join(cols)} FROM endpoints WHERE api_id = ?;
    ''', (api_id, )).fetchall()
    endpoints: List[Endpoint] = []
    for row in rows:
        d: Any = dict()
        for k, v in zip(cols, row):
            d[k] = v
        endpoint = Endpoint(
            id=d['id'],
            title=d['title'],
            location=d['location'],
            method=d['method'],
            api_id=d['api_id'],
            created=datetime.fromisoformat(d['created']),
            updated=datetime.fromisoformat(d['updated']),
        )
        endpoints.append(endpoint)
    return endpoints

def update_endpoint(id: RecordId, title: Optional[str] = None, location: Optional[int] = None, method: Optional[str] = None, api_id: Optional[RecordId] = None, created: Optional[datetime] = None, updated: Optional[datetime] = None) -> None:
    if title is not None:
        cur.execute('''
            UPDATE endpoints SET title = ? WHERE id = ?;
        ''', (title, id, ))
    if location is not None:
        cur.execute('''
            UPDATE endpoints SET location = ? WHERE id = ?;
        ''', (location, id, ))
    if method is not None:
        cur.execute('''
            UPDATE endpoints SET method = ? WHERE id = ?;
        ''', (method, id, ))
    if api_id is not None:
        cur.execute('''
            UPDATE endpoints SET api_id = ? WHERE id = ?;
        ''', (api_id, id, ))
    if created is not None:
        cur.execute('''
            UPDATE endpoints SET created = ? WHERE id = ?;
        ''', (created.isoformat(), id, ))
    if updated is not None:
        cur.execute('''
            UPDATE endpoints SET updated = ? WHERE id = ?;
        ''', (updated.isoformat(), id, ))
    con.commit()

def delete_endpoint(id: RecordId) -> None:
    cur.execute('''
        DELETE FROM endpoints WHERE id = ?;
    ''', (id, ))
    con.commit()


# FIELD

def insert_field(value: str, location: int, endpoint_id: RecordId, created: datetime, updated: datetime) -> Field:
    id = cur.execute('''
        INSERT INTO fields (value, location, endpoint_id, created, updated) VALUES (?, ?, ?, ?, ?);
    ''', (value, location, endpoint_id, created, updated)).lastrowid
    con.commit()
    field = select_field_by_id(id=id)
    if field is None:
        raise ValueError('Unexpected field is None')
    return field

def select_field_by_id(id: RecordId) -> Optional[Field]:
    cols = ['id', 'value', 'location', 'endpoint_id', 'created', 'updated']
    row = cur.execute(f'''
        SELECT {', '.join(cols)} FROM fields WHERE id = ?;
    ''', (id, )).fetchone()
    if row is None:
        return None
    d: Any = dict()
    for k, v in zip(cols, row):
        d[k] = v
    return Field(
        id=d['id'],
        value=d['value'],
        location=d['location'],
        endpoint_id=d['endpoint_id'],
        created=datetime.fromisoformat(d['created']),
        updated=datetime.fromisoformat(d['updated']),
    )

def select_fields_for_endpoint(endpoint_id: RecordId) -> List[Field]:
    cols = ['id', 'value', 'location', 'endpoint_id', 'created', 'updated']
    rows = cur.execute(f'''
        SELECT {', '.join(cols)} FROM fields WHERE endpoint_id = ?;
    ''', (endpoint_id, )).fetchall()
    fields: List[Field] = []
    for row in rows:
        d: Any = dict()
        for k, v in zip(cols, row):
            d[k] = v
        field = Field(
            id=d['id'],
            value=d['value'],
            location=d['location'],
            endpoint_id=d['endpoint_id'],
            created=datetime.fromisoformat(d['created']),
            updated=datetime.fromisoformat(d['updated']),
        )
        fields.append(field)
    return fields

def update_field(id: RecordId, value: Optional[str] = None, location: Optional[int] = None, endpoint_id: Optional[RecordId] = None, created: Optional[datetime] = None, updated: Optional[datetime] = None) -> None:
    if value is not None:
        cur.execute('''
            UPDATE fields SET value = ? WHERE id = ?;
        ''', (value, id, ))
    if location is not None:
        cur.execute('''
            UPDATE fields SET location = ? WHERE id = ?;
        ''', (location, id, ))
    if endpoint_id is not None:
        cur.execute('''
            UPDATE fields SET endpoint_id = ? WHERE id = ?;
        ''', (endpoint_id, id, ))
    if created is not None:
        cur.execute('''
            UPDATE fields SET created = ? WHERE id = ?;
        ''', (created.isoformat(), id, ))
    if updated is not None:
        cur.execute('''
            UPDATE fields SET updated = ? WHERE id = ?;
        ''', (updated.isoformat(), id, ))
    con.commit()

def delete_field(id: RecordId) -> None:
    cur.execute('''
        DELETE FROM fields WHERE id = ?;
    ''', (id, ))
    con.commit()
