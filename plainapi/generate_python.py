from typing import List, TypedDict
import os
from dotenv import load_dotenv
import openai  # type: ignore

from plainapi.parse_endpoint import Endpoint, FunctionInput
from plainapi.parse_application import Application
from plainapi.types import AssignmentStatement, CodeBlock, ExceptionStatement, FunctionCallStatement, IfStatement, OutputStatement, PythonStatement, RightHandSideStatement, SQLStatement


load_dotenv('./.env')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError('Expected OPENAI_API_KEY environment variable to be set or in `.env` file.')
openai.api_key = OPENAI_API_KEY


def url2endpoint_function_name(url: str) -> str:
    clean = ''.join(c if c.isalnum() else ' ' for c in url)
    parts = [s.strip() for s in clean.split(' ') if s.strip() != '']
    return 'endpoint_' + '_'.join(parts)


def string2variable_name(s: str) -> str:
    clean = ''.join(c if c.isalnum() else ' ' for c in s)
    parts = [s.strip() for s in clean.split(' ') if s.strip() != '']
    if len(parts) < 0:
        return '_'
    else:
        return '_'.join(parts)


def escape_quotes(s: str) -> str:
    o = ''
    for c in s:
        if c == '\'':
            o += '\\\''
        elif c == '\"':
            o += '\\\"'
        else:
            o += c
    return o


def generate_right_hand_side_statement(block: RightHandSideStatement) -> str:
    if block['type'] == 'sql':
        return generate_sql_statement(block)
    elif block['type'] == 'python':
        return generate_python_statement(block)
    elif block['type'] == 'function_call':
        return generate_function_call(block)
    else:
        raise ValueError('Internal Error')


def generate_output_statement(block: OutputStatement, indent=0) -> str:
    tab = ' ' * indent
    rhs = generate_right_hand_side_statement(block['value'])
    comment = block['original'].strip()
    return f'{tab}return {rhs}  # {comment}\n'


def generate_sql_statement(block: SQLStatement) -> str:
    sql = block['sql']
    block[]
    columns = [i['name'] for i in block['outputs']]
    return f'sql(\"{sql.strip()}\", columns={columns}, params=[])'


def generate_exception_statement(block: ExceptionStatement, indent=0) -> str:
    tab = ' ' * indent
    code = block['code'] or 400
    message = block['message'] or 'An error has occurred.'
    comment = block['original']
    return f'{tab}raise HTTPException(status_code={code}, detail={message})  # {comment.strip()}\n'


def generate_python_statement(block: PythonStatement) -> str:
    return block['code']


def generate_function_call(block: FunctionCallStatement) -> str:
    return block['function_name'] + '()'


def generate_assigment_statement(block: AssignmentStatement, indent=0) -> str:
    tab = ' ' * indent
    variable_name = string2variable_name(block['name'])
    value = block['value']
    if value['type'] == 'python':
        comment = block['original']
        value_string = generate_python_statement(value)
    elif value['type'] == 'sql':
        comment = block['original']
        value_string = generate_sql_statement(value)
    elif value['type'] == 'function_call':
        comment = block['original']
        value_string = generate_function_call(value)
    else:
        raise ValueError('Internal Error')
    return f'{tab}{variable_name} = {value_string}  # {comment.strip()}\n'


def generate_if_statement(block: IfStatement, indent=0):
    tab = ' ' * indent
    condition = block['condition']['code']
    comment = block['condition']['original']
    text = tab + 'if ' + condition + ':  # ' + comment.strip() + '\n'
    text += generate_code_block(block['case_true'], indent=indent + 4)
    if block['case_false'] is not None:
        text += tab + 'else:\n'
        text += generate_code_block(block['case_false'], indent=indent + 4)
    return text


def generate_code_block(block: CodeBlock, indent=0) -> str:
    tab = ' ' * indent
    text = ''
    for line in block:
        if line['type'] == 'if':
            text += generate_if_statement(line, indent)
        elif line['type'] == 'exception':
            text += generate_exception_statement(line, indent)
        elif line['type'] == 'assignment':
            text += generate_assigment_statement(line, indent)
        elif line['type'] == 'output':
            text += generate_output_statement(line, indent)
        elif line['type'] == 'function_call':
            comment = line['original'].strip()
            text += tab + generate_function_call(line) + f'  # {comment}\n'
        elif line['type'] == 'python':
            comment = line['original'].strip()
            text += tab + generate_python_statement(line) + f'  # {comment}\n'
        elif line['type'] == 'sql':
            comment = line['original'].strip()
            text += tab + generate_sql_statement(line) + f'  # {comment}\n'
        else:
            raise ValueError('Internal Error')
    return text


def generate_endpoint(endpoint: Endpoint, schema_text: str, use_cache=True) -> str:
    """
    Generate a FastAPI endpoint from an SQL query.

    short_name: a name for the query in snake_case
    sql_query: an SQL query

    """

    def gen_params(params: List[FunctionInput]) -> str:
        return ', '.join(i['name'] + ': ' + i['type'] for i in params)

    func_name = url2endpoint_function_name(endpoint['header']['url'])
    url = endpoint['header']['url'].lower()
    method = endpoint['header']['method'].lower()
    contains_current_user = 'current_user' in [i['name'] for i in endpoint['requirements']['inputs']]
    if contains_current_user:
        p = [i for i in endpoint['requirements']['inputs'] if i['name'] != 'current_user'] \
            + [FunctionInput(name='current_user', type='User = Depends(get_current_user)')]
        params = gen_params(p)
    else:
        params = gen_params(endpoint['requirements']['inputs'])
    implementation = generate_code_block(endpoint['implementation'], indent=4)

    outputs = endpoint['requirements']['outputs']
    if len(outputs) == 0:
        response_model = 'None'
    elif len(outputs) == 1:
        response_model = outputs[0]['type']
    else:
        response_model = 'Tuple[{}]'.format(', '.join(i['type'] for i in outputs))

    code = \
f'''@app.{method}("{url}", response_model={response_model})
async def {func_name}({params}):
{implementation}'''

    return code


def generate_app(application: Application, schema_text: str, db_name: str, host: str = 'localhost', port: int = 3000):

    title = application['title']
    code_for_endpoints = '\n\n'.join(generate_endpoint(endpoint, schema_text) for endpoint in application['endpoints'])

    code = \
f'''from typing import List, Union, Literal, Optional, Dict, Any, Tuple
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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

class User(BaseModel):
    id: int
    email: str
    is_admin: bool


con = sqlite3.connect('{db_name}')


def sql(query: str, columns: List[str], params: Any = []):
    rows = con.cursor().execute(query, params)
    dicts = []
    for row in rows:
        dicts.append({{ k: v for k, v in zip(columns, row) }})
    return dicts


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={{"WWW-Authenticate": "Bearer"}},
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


{code_for_endpoints}'''

    return code
