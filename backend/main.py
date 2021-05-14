from typing import List, Optional, cast
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from dotenv import load_dotenv
import jwt
import bcrypt

from models import RecordId, Token, User, UserPublic, API, Endpoint
from utils import expect_env, clean_user
import queries


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
    allow_origins=['http://localhost:3000'],
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
    except:
        raise credentials_exception
    email: Optional[str] = payload.get("sub")
    if email is None:
        raise credentials_exception
    user = queries.select_user_by_email(email=email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_api(api_id: RecordId) -> API:
    api = queries.select_api_by_id(id=api_id)
    if api is None:
        raise HTTPException(status_code=400, detail='No such api')
    return api

r"""
 _   _                   
| | | |                  
| | | |___  ___ _ __ ___ 
| | | / __|/ _ \ '__/ __|
| |_| \__ \  __/ |  \__ \
 \___/|___/\___|_|  |___/

"""

@app.get(PREFIX + "/users/read-by-id/", response_model=UserPublic)
async def read_user(id: RecordId) -> UserPublic:
    user = queries.select_user_by_id(id=id)
    if user is None:
        raise HTTPException(status_code=400, detail='No such user')
    return clean_user(user)

@app.get(PREFIX + "/users/read-by-email/", response_model=UserPublic)
async def read_user_by_email(email: str, current_user: User = Depends(get_current_user)) -> UserPublic:
    if current_user.email != email and not current_user.is_admin:
        raise HTTPException(status_code=401, detail='Unauthorized request')
    user = queries.select_user_by_email(email=email)
    if user is None:
        raise HTTPException(status_code=400, detail='No such user')
    return clean_user(user)

@app.get(PREFIX + "/users/read-all", response_model=List[UserPublic])
async def read_users(current_user: User = Depends(get_current_user)) -> List[UserPublic]:
    if not current_user.is_admin:
        raise HTTPException(status_code=401, detail='Unauthorized request')
    return [clean_user(user) for user in queries.select_all_users()]

@app.post(PREFIX + "/users/signup", response_model=UserPublic)
async def signup_user(email: str, password: str) -> UserPublic:
    existing_user = queries.select_user_by_email(email=email)
    if existing_user is not None:
        raise HTTPException(status_code=400, detail='A user with that email already exists')
    if not is_good_password(password):
        raise HTTPException(status_code=400, detail='Passwords must be at least 8 characters long')
    now = datetime.utcnow()
    hashed_password = str(bcrypt.hashpw(bytes(password, 'utf-8'), bcrypt.gensalt()), 'utf-8')
    user = queries.insert_user(email=email, hashed_password=hashed_password, is_admin=False, joined=now)
    return clean_user(user)

@app.post(PREFIX + "/users/login", response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = queries.select_user_by_email(email=form_data.username)
    if user is None:
        raise HTTPException(status_code=400, detail='Incorrect password or email.')
    if not bcrypt.checkpw(bytes(form_data.password, 'utf-8'), bytes(user.hashed_password, 'utf-8')):
        raise HTTPException(status_code=400, detail='Incorrect password or email.')
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

@app.delete(PREFIX + "/users/delete/", response_model=None)
async def delete_user(id: RecordId, current_user: User = Depends(get_current_user)) -> None:
    if not current_user.is_admin:
        raise HTTPException(status_code=401, detail='Unauthorized request')
    user = queries.select_user_by_id(id=id)
    if user is None:
        raise HTTPException(status_code=400, detail='No such user')
    queries.delete_user(id=id)

r"""
  ___  ______ _____    
 / _ \ | ___ \_   _|   
/ /_\ \| |_/ / | | ___ 
|  _  ||  __/  | |/ __|
| | | || |    _| |\__ \
\_| |_/\_|    \___/___/

"""

@app.post(PREFIX + '/apis/create', response_model=API)
async def create_api(title: str,
                     serialized_endpoints: str,
                     user_id: RecordId,
                     current_user: User = Depends(get_current_user)) -> API:
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=401, detail='Unauthorized request')
    now = datetime.utcnow()
    return queries.insert_api(title=title, serialized_endpoints=serialized_endpoints, user_id=user_id, created=now, updated=now)

@app.get(PREFIX + '/apis/get-by-id/', response_model=API)
async def read_api(current_user: User = Depends(get_current_user),
                   api: API = Depends(get_current_api)) -> API:
    if not current_user.is_admin and current_user.id != api.user_id:
        raise HTTPException(status_code=401, detail='Unauthorized request')
    return api

@app.get(PREFIX + '/apis/get-all-for-user', response_model=List[API])
async def read_apis_for_user(user_id: RecordId,
                             current_user: User = Depends(get_current_user)) -> List[API]:
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(status_code=401, detail='Unauthorized request')
    return queries.select_apis_for_user(user_id=user_id)

@app.patch(PREFIX + '/apis/update/', response_model=None)
async def update_api(title: Optional[str] = None,
                     serialized_endpoints: Optional[str] = None,
                     current_user: User = Depends(get_current_user),
                     api: API = Depends(get_current_api)) -> None:
    if not current_user.is_admin and current_user.id != api.user_id:
        raise HTTPException(status_code=401, detail='Unauthorized request')
    now = datetime.utcnow()
    queries.update_api(id=api.id, title=title, serialized_endpoints=serialized_endpoints, updated=now)

@app.delete(PREFIX + '/apis/delete/', response_model=None)
async def delete_api(current_user: User = Depends(get_current_user), api: API = Depends(get_current_api)) -> None:
    if not current_user.is_admin and current_user.id != api.user_id:
        raise HTTPException(status_code=401, detail='Unauthorized request')
    queries.delete_api(id=api.id)

r"""
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