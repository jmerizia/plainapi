from typing import List, Optional, cast
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from dotenv import load_dotenv
import jwt
import bcrypt

from models import RecordId, Token, User, UserPublic, API, Endpoint, Field
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

async def get_current_endpoint(endpoint_id: RecordId) -> Endpoint:
    endpoint = queries.select_endpoint_by_id(id=endpoint_id)
    if endpoint is None:
        raise HTTPException(status_code=400, detail='No such endpoint')
    return endpoint

async def get_current_field(field_id: RecordId) -> Field:
    field = queries.select_field_by_id(id=field_id)
    if field is None:
        raise HTTPException(status_code=400, detail='No such field')
    return field

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
                     user_id: RecordId,
                     current_user: User = Depends(get_current_user)) -> API:
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=401, detail='Unauthorized request')
    now = datetime.utcnow()
    return queries.insert_api(title=title, user_id=user_id, created=now, updated=now)

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
                     current_user: User = Depends(get_current_user),
                     api: API = Depends(get_current_api)) -> None:
    if not current_user.is_admin and current_user.id != api.user_id:
        raise HTTPException(status_code=401, detail='Unauthorized request')
    now = datetime.utcnow()
    queries.update_api(id=api.id, title=title, updated=now)

@app.delete(PREFIX + '/apis/delete/', response_model=None)
async def delete_api(current_user: User = Depends(get_current_user), api: API = Depends(get_current_api)) -> None:
    if not current_user.is_admin and current_user.id != api.user_id:
        raise HTTPException(status_code=401, detail='Unauthorized request')
    queries.delete_api(id=api.id)

r"""
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
async def create_endpoint(title: str,
                          location: int,
                          method: str,
                          current_user: User = Depends(get_current_user),
                          api: API = Depends(get_current_api)) -> Endpoint:
    if not current_user.is_admin and api.user_id != current_user.id:
        raise HTTPException(status_code=401, detail='Unauthorized')
    print(api.user_id, current_user.id)
    now = datetime.utcnow()
    existing_endpoints = sorted(queries.select_endpoints_for_api(api_id=api.id), key=lambda e: e.location)
    cur = 0
    for endpoint in existing_endpoints:
        if cur == location:
            # skip over this endpoint
            cur += 1
        queries.update_endpoint(id=endpoint.id, location=cur)
        cur += 1
    new_endpoint = queries.insert_endpoint(title=title, api_id=api.id, location=location, method=method, created=now, updated=now)
    return new_endpoint

@app.get(PREFIX + "/endpoint/read/", response_model=Endpoint)
async def read_endpoint(current_user: User = Depends(get_current_user),
                        endpoint: Endpoint = Depends(get_current_endpoint),
                        api: API = Depends(get_current_api)) -> Endpoint:
    if not current_user.is_admin and endpoint.id != api.user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')
    if endpoint.api_id != api.id:
        raise HTTPException(status_code=400, detail='Invalid Request')
    return endpoint

@app.get(PREFIX + "/endpoint/read-all-for-api", response_model=List[Endpoint])
async def read_endpoints_for_api(current_user: User = Depends(get_current_user),
                                 api: API = Depends(get_current_api)) -> List[Endpoint]:
    if not current_user.is_admin and api.user_id != current_user.id:
        raise HTTPException(status_code=401, detail='Unauthorized')
    endpoints = queries.select_endpoints_for_api(api_id=api.id)
    return endpoints

@app.patch(PREFIX + "/endpoint/update/", response_model=None)
async def update_endpoint(title: Optional[str] = None,
                          location: Optional[int] = None,
                          method: Optional[str] = None,
                          current_user: User = Depends(get_current_user),
                          endpoint: Endpoint = Depends(get_current_endpoint),
                          api: API = Depends(get_current_api)) -> None:
    if not current_user.is_admin and api.user_id != current_user.id:
        raise HTTPException(status_code=401, detail='Unauthorized')
    if endpoint.api_id != api.id:
        raise HTTPException(status_code=400, detail='Invalid Request')
    now = datetime.utcnow()
    queries.update_endpoint(id=endpoint.id, title=title, location=location, method=method, updated=now)

@app.delete(PREFIX + "/endpoint/delete/", response_model=None)
async def delete_endpoint(current_user: User = Depends(get_current_user),
                          endpoint: Endpoint = Depends(get_current_endpoint),
                          api: API = Depends(get_current_api)) -> None:
    if not current_user.is_admin and api.user_id != current_user.id:
        raise HTTPException(status_code=401, detail='Unauthorized')
    if endpoint.api_id != api.id:
        raise HTTPException(status_code=400, detail='Invalid Request')
    queries.delete_endpoint(id=endpoint.id)

r"""
______ _      _     _     
|  ___(_)    | |   | |    
| |_   _  ___| | __| |___ 
|  _| | |/ _ \ |/ _` / __|
| |   | |  __/ | (_| \__ \
\_|   |_|\___|_|\__,_|___/
                          
"""

@app.post(PREFIX + "/field/create", response_model=Field)
async def create_field(value: str,
                       location: int,
                       current_user: User = Depends(get_current_user),
                       endpoint: Endpoint = Depends(get_current_endpoint),
                       api: API = Depends(get_current_api)) -> Field:
    if not current_user.is_admin and current_user.id != api.user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')
    if endpoint.api_id != api.id:
        raise HTTPException(status_code=400, detail='Invalid Request')
    now = datetime.utcnow()
    existing_fields = sorted(queries.select_fields_for_endpoint(endpoint_id=endpoint.id), key=lambda f: f.location)
    cur = 0
    for field in existing_fields:
        if cur == location:
            # skip over field
            cur += 1
        queries.update_field(id=field.id, location=cur)
        cur += 1
    new_field = queries.insert_field(value=value, location=cur, endpoint_id=endpoint.id, created=now, updated=now)
    return new_field

@app.get(PREFIX + "/field/read", response_model=Field)
async def read_field(current_user: User = Depends(get_current_user),
                     field: Field = Depends(get_current_field),
                     endpoint: Endpoint = Depends(get_current_endpoint),
                     api: API = Depends(get_current_api)) -> Field:
    if not current_user.is_admin and current_user.id != api.user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')
    if endpoint.api_id != api.id:
        raise HTTPException(status_code=400, detail='Invalid Request')
    if field.endpoint_id != endpoint.id:
        raise HTTPException(status_code=400, detail='Invalid Request')
    return field

@app.get(PREFIX + "/field/read-for-endpoint", response_model=List[Field])
async def read_fields_for_endpoint(current_user: User = Depends(get_current_user),
                                   endpoint: Endpoint = Depends(get_current_endpoint),
                                   api: API = Depends(get_current_api)) -> List[Field]:
    if not current_user.is_admin and current_user.id != api.user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')
    if endpoint.api_id != api.id:
        raise HTTPException(status_code=400, detail='Invalid Request')
    return queries.select_fields_for_endpoint(endpoint_id=endpoint.id)

@app.patch(PREFIX + "/field/update/", response_model=None)
async def update_field(value: Optional[str] = None,
                       location: Optional[int] = None,
                       current_user: User = Depends(get_current_user),
                       endpoint: Endpoint = Depends(get_current_endpoint),
                       api: API = Depends(get_current_api),
                       field: Field = Depends(get_current_field)) -> None:
    if not current_user.is_admin and current_user.id != api.user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')
    if endpoint.api_id != api.id:
        raise HTTPException(status_code=400, detail='Invalid Request')
    if field.endpoint_id != endpoint.id:
        raise HTTPException(status_code=400, detail='Invalid Request')
    now = datetime.utcnow()
    queries.update_field(id=field.id, value=value, location=location, updated=now)

@app.delete(PREFIX + "/field/delete/", response_model=None)
async def delete_field(current_user: User = Depends(get_current_user),
                       endpoint: Endpoint = Depends(get_current_endpoint),
                       api: API = Depends(get_current_api),
                       field: Field = Depends(get_current_field)) -> None:
    if not current_user.is_admin and current_user.id != api.user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')
    if endpoint.api_id != api.id:
        raise HTTPException(status_code=400, detail='Invalid Request')
    if field.endpoint_id != endpoint.id:
        raise HTTPException(status_code=400, detail='Invalid Request')
    queries.delete_field(id=field.id)

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