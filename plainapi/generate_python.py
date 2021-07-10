from typing import TypedDict
import os
from dotenv import load_dotenv
import openai  # type: ignore

from plainapi.parse_endpoint import Endpoint
from plainapi.parse_application import Application


load_dotenv('./.env')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError('Expected OPENAI_API_KEY environment variable to be set or in `.env` file.')
openai.api_key = OPENAI_API_KEY


def url2endpoint_function_name(url: str) -> str:
    clean = ''.join(c if c.isalnum() else ' ' for c in url)
    parts = [s.strip() for s in clean.split(' ') if s.strip() != '']
    return 'endpoint_' + '_'.join(parts)


def generate_endpoint(endpoint: Endpoint, schema_text: str, use_cache=True) -> str:
    """
    Generate a FastAPI endpoint from an SQL query.

    short_name: a name for the query in snake_case
    sql_query: an SQL query

    """

    func_name = url2endpoint_function_name(endpoint['header']['url'])
    url = endpoint['header']['url'].lower()
    method = endpoint['header']['method'].lower()
    params = ', '.join(s['name'] + ': ' + s['type'] for s in endpoint['requirements']['inputs'])
    implementation = endpoint['implementation']

    code = \
f'''@app.{method}("{url}", response_model=None)
async def {func_name}({params}) -> None:
    \'\'\'
    {implementation}
    \'\'\'
    pass'''

    return code


def generate_app(application: Application, schema_text: str, db_name: str, host: str = 'localhost', port: int = 3000):

    title = application['title']
    code_for_endpoints = '\n\n\n'.join(generate_endpoint(endpoint, schema_text) for endpoint in application['endpoints'])

    code = \
f'''from typing import List, Union, Literal, Optional, Dict, Any
from fastapi import FastAPI, Path, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sqlite3


app = FastAPI(
    title="{title}",
    description="An API generated from English sentences",
    version="0.1.0",
    docs_url="/docs"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://{host}:{port}'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

con = sqlite3.connect('{db_name}')


{code_for_endpoints}'''

    return code
