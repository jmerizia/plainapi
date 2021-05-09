from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import jwt
from typing import Optional
import boto3
import json
import random
import os

from models import RecordId, Token, User


"""
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

load_dotenv()
APP_ROOT_URL   = expect_env("APP_ROOT_URL")
