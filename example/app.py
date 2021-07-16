from typing import List, Union, Literal, Optional, Dict, Any
from fastapi import FastAPI, Path, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
import os
import sqlite3

ALGORITHM = "HS256"
SECRET_KEY = "TODO"

app = FastAPI(
    title="My API",
    description="An API generated from English sentences",
    version="0.1.0",
    docs_url="/docs"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

class User(BaseModel):
    id: int
    email: str
    is_admin: bool


def sql(query: str, params: Any):
    # TODO
    return None


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
    user = sql("select * from users where email = ?", [email])
    if user is None:
        raise credentials_exception
    return user


con = sqlite3.connect('my-app.sqlite3')


@app.get("/users/{id}", response_model=None)
async def endpoint_users_id(id: str) -> None:
    user = user = sql.get(id)
    if user == None:  # if user is not defined
        raise HTTPException(status_code=400, detail="No such user")
    else:
        user = user = user.copy()
        return user


@app.get("/users/with-email/{email}", response_model=None)
async def endpoint_users_with_email_email(current_user: User = Depends(get_current_user)) -> None:
    if current_user.is_admin == False:  # if the current user is not an admin
        raise HTTPException(status_code=400, detail="Forbidden")
    user = user = sql.get_user(email=email)
    if user == None:  # if user is not defined
        raise HTTPException(status_code=400, detail="No such user")
    else:
        return user


@app.get("/users", response_model=None)
async def endpoint_users(current_user: User = Depends(get_current_user)) -> None:
    if current_user.is_admin == False:  # if the current user is not an admin
        raise HTTPException(status_code=400, detail="Forbidden")
    return all the users from the db


@app.get("/users/email/{id}", response_model=None)
async def endpoint_users_email_id(current_user: User = Depends(get_current_user)) -> None:
    if current_user.is_admin != True and current_user.id != id:  # if the current user is not an admin and their id is not equal to {id}
        raise HTTPException(status_code=400, detail="Forbidden")
    return sql: the email of the user with id {id}


@app.post("/users/signup", response_model=None)
async def endpoint_users_signup(email: str, password: str) -> None:
    existing_user = user = sql(email).get()
    if user:  # if existing user is defined
        raise HTTPException(status_code=400, detail="A user with that email already exists")
    if password != "good password":  # if {password} is not a good password
        raise HTTPException(status_code=400, detail="Bad password")
    hashed_password = hash(func(password))
    nickname = nickname = func()
    now = now = func()
    new_user = new_user = func(nickname, now, email, verified=False, score=0)
     = func(email, nickname)
    return {new user}


@app.post("/users/login", response_model=None)
async def endpoint_users_login(email: str, password: str) -> None:
    user = user = sql(email == email)
    if user == None:  # if user is not defined
        raise HTTPException(status_code=400, detail="Invalid email or password")
    if password != user.password:  # if the {password} doesn't match the user's hashed password
        raise HTTPException(status_code=400, detail="Invalid email or password")
    token = token = jwt.encode({'sub': email, 'exp': 30 * 24 * 60 * 60}, secret)
    return {token}, {token_type}, {id}
