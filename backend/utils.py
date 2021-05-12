from typing import List, Dict, Generic, TypeVar
import os

from models import Endpoint, Field, RecordId, User, UserPublic

T = TypeVar('T')

r"""
 _   _ _   _ _     
| | | | | (_) |    
| | | | |_ _| |___ 
| | | | __| | / __|
| |_| | |_| | \__ \
 \___/ \__|_|_|___/
                   
"""

def expect_env(varname: str) -> str:
    val = os.getenv(varname)
    if val is None or val == "":
        raise ValueError(f"Missing environment variable ${varname}")
    else:
        result: str = val
        return result

def clean_user(user: User) -> UserPublic:
    return UserPublic(
        id=user.id,
        is_admin=user.is_admin,
        joined=user.joined
    )
