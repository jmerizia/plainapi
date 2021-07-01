from typing import List, Union, Literal, Optional, Dict, Any
from fastapi import FastAPI, Path, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sqlite3


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

con = sqlite3.connect('my-app.sqlite3')


@app.get("/users/{id}", response_model=None)
async def endpoint_users_id(user: Any) -> None:
    '''
    if user is not defined
    report 400: "No such user"
otherwise
    remove the email field from user
    return user
    '''
    pass


@app.get("/users/with-email/{email}", response_model=None)
async def endpoint_users_with_email_email(auth: Any) -> None:
    '''
        if the current user is not an admin
        report 400: "Forbidden"
    user <- get a user with email {email}
    if user is not defined
        report 400: No such user
    otherwise
        return user
    '''
    pass


@app.get("/users", response_model=None)
async def endpoint_users(auth: Any) -> None:
    '''
        if the current user is not an admin
        report 400: "Forbidden"
    report all the users from the db
    '''
    pass


@app.get("/users/email/{id}", response_model=None)
async def endpoint_users_email_id(auth: Any) -> None:
    '''
        if the current user is not an admin and their id is not equal to {id}
        report 400 "Forbidden"
    return the email of the user with id {id}
    '''
    pass


@app.post("/users/signup", response_model=None)
async def endpoint_users_signup(email: str, password: str) -> None:
    '''
        existing user <- get a user with email equal to {email}
    if existing user is defined
        report "A user with that email already exists"
    if {password} is not a good password
        report "Bad password"
    hashed password <- hash {password}
    nickname <- get a random name
    now <- get the current utc time
    new user <- create a new user (not admin) with nickname = {nickname}, created and updated set to {now}, email set to {email}, verified set to false, and a score of 0
    send verification email to {email} with {nickname}
    return {new user}
    '''
    pass


@app.post("/users/login", response_model=None)
async def endpoint_users_login(email: str, password: str) -> None:
    '''
        user <- get a user with email equal to {email}
    if user is not defined
        report "Invalid email or password"
    if the {password} doesn't match the user's hashed password
        report "Invalid email or password"
    token <- create a JWT token with sub = {email} and exp = 30 days from now
    return an object with access_token = {token}, token_type = "bearer", and id = the user's id
    '''
    pass
