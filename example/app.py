from typing import List, Union, Literal, Optional, Dict, Any, Tuple
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


con = sqlite3.connect('my-app.sqlite3')


def sql(query: str, params: Any = []):
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


@app.get("/users/{id}", response_model=)
async def endpoint_users_id(id: str):
    user = sql("SELECT * FROM users WHERE id = ?")  # user <- sql: get a user with id {id}
    if user == None:  # if user is not defined
        raise HTTPException(status_code=400, detail="No such user")  # report 400: "No such user"
    else:
        user = user.__dict__.pop("email")  # user <- user without the email field
        return user  # return user


@app.get("/users/with-email/{email}", response_model=Tuple[str, str])
async def endpoint_users_with_email_email(email: str, id: str, current_user: User = Depends(get_current_user)):
    if current_user.is_admin == False:  # if the current user is not an admin
        raise HTTPException(status_code=400, detail="Forbidden")  # report 400: "Forbidden"
    user = sql("SELECT * FROM users WHERE email = ?")  # user <- sql: get a user with email {email}
    if user == None:  # if user is not defined
        raise HTTPException(status_code=400, detail="No such user")  # raise 400: No such user
    else:
        return user  # return {user}


@app.get("/users", response_model=str)
async def endpoint_users(current_user: User = Depends(get_current_user)):
    if current_user.is_admin == False:  # if the current user is not an admin
        raise HTTPException(status_code=400, detail="Forbidden")  # report 400: "Forbidden"
    return sql("SELECT * FROM users")  # report sql: all the users from the db


@app.get("/users/email/{id}", response_model=Tuple[int, str])
async def endpoint_users_email_id(id: str, current_user: User = Depends(get_current_user)):
    if current_user.is_admin != True and current_user.id != id:  # if the current user is not an admin and their id is not equal to {id}
        raise HTTPException(status_code=400, detail="Forbidden")  # report 400 "Forbidden"
    return sql("SELECT email FROM users WHERE id = ?")  # return sql: the email of the user with id {id}


@app.post("/users/signup", response_model=Tuple[str, str])
async def endpoint_users_signup(email: str, password: str):
    existing_user = sql("SELECT * FROM users WHERE email = ?")  # existing user <- sql: get a user with email equal to {email}
    if existing_user is not None:  # if existing user is defined
        raise HTTPException(status_code=400, detail="A user with that email already exists")  # report "A user with that email already exists"
    if password != "good password":  # if {password} is not a good password
        raise HTTPException(status_code=400, detail="Bad password")  # report "Bad password"
    hashed_password = TODO()  # hashed password <- func: hash {password}
    nickname = TODO()  # nickname <- func: get a random name
    now = TODO()  # now <- func: get the current utc time
    new_user = sql("INSERT INTO users (nickname, created, updated, email, verified, score) VALUES (?, ?, ?, ?, false, 0)")  # new user <- sql: create a new user (not admin) with nickname = {nickname}, created and updated set to {now}, email set to {email}, verified set to false, and a score of 0
    TODO()  # func: send verification email to {email} with {nickname}
    return new_user  # return {new user}


@app.post("/users/login", response_model=Tuple[str, str])
async def endpoint_users_login(email: str, password: str):
    user = sql("SELECT * FROM users WHERE email = ?")  # user <- sql: get a user with email equal to {email}
    if user == None:  # if user is not defined
        raise HTTPException(status_code=400, detail="Invalid email or password")  # report "Invalid email or password"
    if password != user.password_hash:  # if the {password} doesn't match the user's hashed password
        raise HTTPException(status_code=400, detail="Invalid email or password")  # report "Invalid email or password"
    token = TODO()  # token <- func: create a JWT token with sub = {email} and exp = 30 days from now
    return {"access_token": token, "token_type": "bearer", "id": user.id}  # return an object with access_token = {token}, token_type = "bearer", and id = the user's id


@app.delete("/users/delete/{id}", response_model=Tuple[int, str])
async def endpoint_users_delete_id(id: str, current_user: User = Depends(get_current_user)):
    user = sql("SELECT * FROM users WHERE id = ?")  # user <- sql: get a user with id equal to {id}
    if user is None or user.id != current_user.id:  # if user is not defined or user's id is not equal to the current user's id
        raise HTTPException(status_code=400, detail="Invalid request")  # report "Invalid request"
    sql("DELETE FROM users WHERE id = ?")  # sql: delete the user with id {id}
    return "Ok"  # return "Ok"
