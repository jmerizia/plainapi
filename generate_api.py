import sqlite3
from typing import List, Tuple
from parse_sqlite import get_select_stmt_output_type
import os
import subprocess
import pprint
from fire import Fire
from dotenv import load_dotenv
import openai
from uuid import uuid4


load_dotenv()
openai.api_key = os.getenv('OPENAI_KEY')


def cached_gpt3(prompt: str, stop: str = '\n', use_cache: bool = True) -> str:
    try:
        os.mkdir('cache')
    except:
        pass

    if use_cache:
        # Check the cache
        separator = '\n===========\n'
        cache_files = [os.path.join('cache', p) for p in os.listdir('cache')]
        for fn in cache_files:
            with open(fn, 'r') as f:
                query, result = f.read().split(separator)
            if query == prompt:
                return result

    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=64,
        temperature=0,
        stop=stop,
    )
    result = response['choices'][0]['text']
    
    # Add to the cache
    cache_file = os.path.join('cache', str(uuid4()))
    with open(cache_file, 'w') as f:
        f.write(prompt + separator + result)

    return result

def get_db_schema_text() -> str:
    """
    Get the schema of an SQL query.

    """

    return str(subprocess.check_output(['sqlite3', 'demo.db', '.schema']), 'utf-8')


def english2sql(english_query: str, use_cache: bool = True) -> str:
    """
    Convert a query written in english to an SQL query.

    """

    prompt = '''Q: Show me all of the users
A: SELECT * FROM users;
Q: Show me all the users ordered by age ascending
A: SELECT * FROM users ORDER BY age ASC;
Q: Who is the oldest user?
A: SELECT * FROM users ORDER BY age DESC LIMIT 1;
Q: What are the names of the 10 youngest users?
A: SELECT name FROM users ORDER BY age ASC LIMIT 1;
Q: Who is the oldest person?
A: SELECT * FROM users ORDER BY age DESC LIMIT 1;
Q: get all the users that are located in the United Kingdom
A: SELECT * FROM users WHERE location = 'United Kingdom';
Q: get users of ages between 30 and 40?
A: SELECT * FROM users WHERE age BETWEEN '30' AND '40';
Q: How many users are there?
A: SELECT COUNT(*) FROM users;
Q: Where does user Betty live?
A: SELECT location FROM users WHERE name = 'Betty';
Q: What is Jennifer's age?
A: SELECT age FROM users WHERE name = 'Jennifer';
Q: the average age
A: SELECT AVG(age) FROM users;
Q: the age of the oldest user
A: SELECT MAX(age) FROM users;
Q: the name of the oldest person
A: SELECT name FROM users ORDER BY age DESC LIMIT 1;
Q: the top 10 oldest users
A: SELECT * FROM users ORDER BY age DESC LIMIT 10;
Q: how many admin users are there?
A: SELECT COUNT(*) FROM users WHERE is_admin = TRUE;
Q: retrieve the email of the youngest admin
A: SELECT email FROM users WHERE is_admin = true ORDER BY age ASC LIMIT 1;
Q: get a user by their email
A: SELECT * FROM users WHERE email = ?;
Q: get all users' emails that live at a certain location
A: SELECT * FROM users WHERE location = ?;
Q: '''

    prompt += english_query.strip()
    prompt += '\nA:'

    return cached_gpt3(prompt, use_cache=use_cache).strip()


def english2summary_name(english_query: str, use_cache: bool = True) -> str:
    """
    Convert a query written in English to a short snake_case name

    """

    prompt = '''Q: Show me all of the users
Q: Show me all the users ordered by age ascending
A: get all users ordered by age ascending
Q: Who is the oldest user?
A: get oldest user
Q: What are the names of the 10 youngest users?
A: get ten youngest users
Q: Who is the oldest person?
A: get oldest user
Q: get all the users that are located in the United Kingdom
A: get users from united kingdom
Q: get users of ages between 30 and 40?
A: get users ages between 30 and 40
Q: How many users are there?
A: get number users
Q: Where does user Betty live?
A: get betty location
Q: What is Jennifer's age?
A: get jennifer age
Q: the average age
A: get average user age
Q: the age of the oldest user
A: get age of oldest user
Q: the name of the oldest person
A: get name of oldest user
Q: the top 10 oldest users
A: get ten oldest users
Q: how many admin users are there?
A: get number admin users
Q: retrieve the email of the youngest admin
A: get email of youngest admin user
Q: get a user by their email
A: get user by email
Q: get all users' emails that live at a certain location
A: get users by location
Q: '''

    prompt += english_query.strip()
    prompt += '\nA:'

    result = cached_gpt3(prompt, use_cache=use_cache)

    return '_'.join(result.strip().lower().split(' '))


def generate_endpoint(name: str,
                      sql_query: str,
                      original_english_query: str,
                      schema_text: str) -> str:
    """
    Generate a FastAPI endpoint from an SQL query.

    short_name: a name for the query in snake_case
    sql_query: an SQL query

    """

    template = '''
class OutputType_<<<NAME>>>(BaseModel):
<<<OUTPUT_TYPES>>>

@app.post("/<<<NAME>>>", response_model=List[OutputType_<<<NAME>>>])
async def <<<NAME>>>(<<<PARAMS>>>) -> List[OutputType_<<<NAME>>>]:
    \'\'\'
    <<<ENGLISH_QUERY>>>
    ---
    SQL: <<<SQL_QUERY>>>
    \'\'\'
    cur = con.cursor()
    cur.execute('<<<SQL_QUERY>>>', <<<BINDINGS>>>)
    res = []
    output_names = <<<OUTPUT_NAME_LIST>>>
    for row in cur.fetchall():
        row_dict = dict()
        for k, v in zip(output_names, row):
            row_dict[k] = v
        res.append(row_dict)
    return res
    '''

    inputs, outputs = get_select_stmt_output_type(sql_query, schema_text)

    params = ', '.join(f'{c["name"]}: {c["type"]}' for c in inputs)
    output_types = '    ' + '\n    '.join(f'{c["name"]}: {c["type"]}' for c in outputs)
    if len(inputs) > 0:
        bindings = '(' + ', '.join(c["name"] for c in inputs) + ',)'
    else:
        bindings = ''
    output_name_list = '[' + ', '.join([f'\'{c["name"]}\'' for c in outputs]) + ']'

    template = template.replace('<<<NAME>>>', name)
    template = template.replace('<<<SQL_QUERY>>>', sql_query)
    template = template.replace('<<<OUTPUT_TYPES>>>', output_types)
    template = template.replace('<<<PARAMS>>>', params)
    template = template.replace('<<<ENGLISH_QUERY>>>', original_english_query)
    template = template.replace('<<<BINDINGS>>>', bindings)
    template = template.replace('<<<OUTPUT_NAME_LIST>>>', output_name_list)
    return template


def generate_app_from_english_queries(english_queries: List[str], use_cache: bool = True):

    code = '''
from typing import List, Union, Literal, Optional, Dict
from fastapi import FastAPI, Path, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sqlite3

app = FastAPI(
    title="PlainAPI Demo",
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

con = sqlite3.connect('demo.db')

    '''

    schema_text = get_db_schema_text()
    query_names = [english2summary_name(q, use_cache=use_cache) for q in english_queries]
    sql_queries = [english2sql(q, use_cache=use_cache) for q in english_queries]

    for name, query, english_query in zip(query_names, sql_queries, english_queries):
        endpoint = generate_endpoint(name, query, english_query, schema_text)
        code += endpoint

    return code


def generate_app(input_fn: str = 'queries.txt', output_fn: str = 'api.py', use_cache: bool = True):
    """
    Given a file of English sentences, output a file containing a FastAPI web server.

    """

    with open(input_fn, 'r') as f:
        queries = f.read().split('\n\n')

    queries = [q.strip() for q in queries]
    queries = [q for q in queries if len(q) > 0]
    print('Queries:')
    for query in queries:
        print(f' -> {query}')

    code = generate_app_from_english_queries(queries)
    with open(output_fn, 'w') as f:
        f.write(code)

    command_to_run = 'uvicorn ' + output_fn.split('.')[0] + ':app'
    print(f'Successfully created API! Try running `{command_to_run}`')


if __name__ == '__main__':
    Fire(generate_app)
