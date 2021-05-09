from typing import List, Union, Literal, Optional, Dict
from fastapi import FastAPI, Path, HTTPException, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import JWTError, jwt
from pydantic import BaseModel
import bcrypt
import json
import os

from models import RecordId, StringWrapper, Token, User, Endpoint, Field
from utils import expect_env


load_dotenv()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 60*24*30
PREFIX = "/api/v0"
SECRET_KEY = expect_env("SECRET_KEY")

app = FastAPI(
    title="PlainAPI",
    description="Create APIs with plain English",
    version="0.1.0",
    docs_url=PREFIX + "/docs"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3014'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=PREFIX + "/users/login")

def is_good_password(password: str) -> bool:
    return len(password) >= 8

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise credentials_exception
    email: Optional[str] = payload.get("sub")
    if email is None:
        raise credentials_exception
    user = session.query(ORMUser).filter_by(email=email).first()
    if user is None:
        raise credentials_exception
    return orm_user_to_pydantic(user)

async def get_current_user_verified(user: User = Depends(get_current_user)) -> User:
    unverified_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email address not verified",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not user.verified:
        raise unverified_exception
    return user

"""
 _   _                   
| | | |                  
| | | |___  ___ _ __ ___ 
| | | / __|/ _ \ '__/ __|
| |_| \__ \  __/ |  \__ \
 \___/|___/\___|_|  |___/

"""

@app.get(PREFIX + "/users/{id}", response_model=User)
async def read_user(id: RecordId) -> User:
    user = session.query(ORMUser).filter_by(id=id).first()
    if user is None:
        raise HTTPException(status_code=400, detail='No such user')
    return orm_user_to_pydantic(user)

@app.get(PREFIX + "/users/with-email/{email}", response_model=User)
async def read_user_by_email(email: str) -> User:
    user = session.query(ORMUser).filter_by(email=email).first()
    if user is None:
        raise HTTPException(status_code=400, detail='No such user')
    return orm_user_to_pydantic(user)

@app.get(PREFIX + "/users", response_model=List[User])
async def read_users(current_user: User = Depends(get_current_user_verified)) -> List[User]:
    users = session.query(ORMUser).all()
    return [orm_user_to_pydantic(user) for user in users]

@app.get(PREFIX + "/users-private", response_model=List[User])
async def read_users_private(current_user: User = Depends(get_current_user_verified)) -> List[User]:
    # Only admin can get user emails
    if not current_user.is_admin:
        raise HTTPException(status_code=401, detail='Unauthorized')
    users = session.query(ORMUser).all()
    return [orm_user_private_to_pydantic(user) for user in users]

@app.post(PREFIX + "/users/signup", response_model=User)
async def signup_user(email: str, password: str) -> User:
    existing_user = session.query(ORMUser).filter_by(email=email).first()
    if existing_user is not None:
        raise HTTPException(status_code=400, detail='A user with that email already exists')
    if not is_good_password(password):
        raise HTTPException(status_code=400, detail='Passwords must be at least 8 characters long')
    nickname = random_nickname()
    now = datetime.utcnow()
    hashed_password = str(bcrypt.hashpw(bytes(password, 'utf-8'), bcrypt.gensalt()), 'utf-8')
    user = ORMUser(email=email,
                   nickname=nickname,
                   score=0,
                   is_admin=False,
                   verified=False,
                   hashed_password=hashed_password,
                   created=now,
                   updated=now)
    session.add(user)
    session.commit()
    return orm_user_to_pydantic(user)

@app.post(PREFIX + "/users/login", response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = session.query(ORMUser).filter_by(email=form_data.username).first()
    if user is None:
        raise HTTPException(status_code=400, detail='Incorrect password or email.')
    if not bcrypt.checkpw(bytes(form_data.password, 'utf-8'), bytes(user.hashed_password, 'utf-8')):
        raise HTTPException(status_code=400, detail='Incorrect password or email.')
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    data = {
        "sub": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    }
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return Token(
        access_token=encoded_jwt,
        token_type="bearer",
        id=user.id
    )

@app.patch(PREFIX + "/users/{id}", response_model=None)
async def update_user(id: RecordId, nickname: Optional[str] = None, current_user: User = Depends(get_current_user_verified)) -> None:
    user = session.query(ORMUser).filter_by(id=id).first()
    if user is None:
        raise HTTPException(status_code=400, detail='No such user')
    # Users can only edit themselves, unless they are admins
    if not current_user.is_admin and current_user.id != user.id:
        raise HTTPException(status_code=401, detail='Unauthorized request')
    if nickname is not None:
        existing_user = session.query(ORMUser).filter_by(nickname=nickname).first()
        if existing_user:
            raise HTTPException(status_code=400, detail='User with that nickname exists')
        user.nickname = nickname
        user.updated = datetime.utcnow()
    session.commit()

@app.delete(PREFIX + "/users/{id}", response_model=None)
async def delete_user(id: RecordId, current_user: User = Depends(get_current_user_verified)) -> None:
    user: Optional[ORMUser] = session.query(ORMUser).filter_by(id=id).first()
    if user is None:
        raise HTTPException(status_code=400, detail='No such user')
    # Users can only delete themselves, unless they are admins
    if current_user.id != user.id or not current_user.is_admin:
        raise HTTPException(status_code=401, detail='Unauthorized request')
    session.delete(user)
    session.commit()

@app.patch(PREFIX + "/users/make-admin/{id}", response_model=None)
async def make_user_admin(id: RecordId, current_user: User = Depends(get_current_user_verified)) -> None:
    # Only admins can make other people admin
    if not current_user.is_admin:
        raise HTTPException(status_code=401, detail='Unauthorized')
    user = session.query(ORMUser).filter_by(id=id).first()
    if user is None:
        raise HTTPException(status_code=400, detail='No such user')
    user.is_admin = True
    user.updated = datetime.utcnow()
    session.commit()

@app.patch(PREFIX + "/users/remove-admin/{id}", response_model=None)
async def remove_user_admin(id: RecordId, current_user: User = Depends(get_current_user_verified)) -> None:
    # Only admins can remove other admins
    if not current_user.is_admin:
        raise HTTPException(status_code=401, detail='Unauthorized')
    user = session.query(ORMUser).filter_by(id=id).first()
    if user is None:
        raise HTTPException(status_code=400, detail='No such user')
    # Thomas + Jacob are always admin
    if user.email in SUPERUSERS:
        raise HTTPException(status_code=401, detail='Unauthorized')
    user.is_admin = False
    user.updated = datetime.utcnow()
    session.commit()

@app.patch(PREFIX + "/users/verify/{token}", response_model=StringWrapper)
async def verify_user(token: str, current_user: User = Depends(get_current_user)) -> StringWrapper:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = session.query(ORMUser).filter_by(id=current_user.id).first()
    if not user:
        raise credentials_exception
    try:
        payload = jwt.decode(token, EMAIL_SECRET, algorithms=[ALGORITHM])
    except JWTError:
        raise credentials_exception
    email: Optional[str] = payload.get("sub")
    if email is None:
        raise credentials_exception
    token_user = session.query(ORMUser).filter_by(email=email).first()
    if token_user is None:
        raise credentials_exception
    if token_user.email != user.email:
        raise credentials_exception
    if token_user.verified:
        return StringWrapper(s="AlreadyVerified")
    user.verified = True
    session.commit()

    return StringWrapper(s="Ok")

"""
 _____          _             _       _       
|  ___|        | |           (_)     | |      
| |__ _ __   __| |_ __   ___  _ _ __ | |_ ___ 
|  __| '_ \ / _` | '_ \ / _ \| | '_ \| __/ __|
| |__| | | | (_| | |_) | (_) | | | | | |_\__ \
\____/_| |_|\__,_| .__/ \___/|_|_| |_|\__|___/
                 | |                          
                 |_|                          
"""

@app.post(PREFIX + "/endpoint/create", response_model=Endpoint)
async def create_endpoint(current_user: User = Depends(get_current_user)) -> Endpoint:
    pass

@app.get(PREFIX + "/endpoint/read/{id}", response_model=Endpoint)
async def read_endpoint(id: RecordId, current_user: User = Depends(get_current_user)) -> Endpoint:
    pass

@app.get(PREFIX + "/endpoint/read-all", response_model=List[Endpoint])
async def read_endpoints(current_user: User = Depends(get_current_user)) -> List[Endpoint]:
    pass

@app.patch(PREFIX + "/endpoint/update/{id}", response_model=None)
async def update_endpoint(id: RecordId, current_user: User = Depends(get_current_user)) -> None:
    pass

@app.delete(PREFIX + "/endpoint/delete/{id}", response_model=None)
async def delete_endpoint(id: RecordId, current_user: User = Depends(get_current_user)) -> None:
    pass

"""
______ _      _     _     
|  ___(_)    | |   | |    
| |_   _  ___| | __| |___ 
|  _| | |/ _ \ |/ _` / __|
| |   | |  __/ | (_| \__ \
\_|   |_|\___|_|\__,_|___/
                          
"""

@app.post(PREFIX + "/field/create", response_model=Field)
async def create_field(current_user: User = Depends(get_current_user)) -> Field:
    pass

@app.get(PREFIX + "/field/read/{id}", response_model=Field)
async def read_field(id: RecordId, current_user: User = Depends(get_current_user)) -> Field:
    pass

@app.get(PREFIX + "/field/read-bulk", response_model=List[Field])
async def read_fields(current_user: User = Depends(get_current_user)) -> List[Field]:
    pass

@app.patch(PREFIX + "/field/update/{id}", response_model=None)
async def update_field(id: RecordId, current_user: User = Depends(get_current_user)) -> None:
    pass

@app.delete(PREFIX + "/field/delete/{id}")
async def delete_field(id: RecordId, current_user: User = Depends(get_current_user)) -> None:
    pass

"""
           _          
          (_)         
 _ __ ___  _ ___  ___ 
| '_ ` _ \| / __|/ __|
| | | | | | \__ \ (__ 
|_| |_| |_|_|___/\___|
                      
"""

@app.post(PREFIX + "/log_ui_error", response_model=None)
async def log_ui_error(error_info: str) -> None:
    print(datetime.now(), 'UI Error:', error_info, flush=True)