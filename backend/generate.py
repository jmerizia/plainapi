import sqlite3
from typing import List, Tuple, Optional, Any
from parse_sql import parse_query, parse_schema, type_hint2schema_type
import os
import subprocess
import pprint
from fire import Fire
from dotenv import load_dotenv
import openai
from uuid import uuid4
import sqlite3
import random

from models import Endpoint


load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
DB_NAME = 'generated/demo.sqlite3'
CACHE_DIR = 'gpt_cache'


def cached_gpt3(prompt: str, stop: str = '\n', use_cache: bool = True) -> str:
    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    if use_cache:
        # Check the cache
        separator = '\n===========\n'
        cache_files = [os.path.join(CACHE_DIR, p) for p in os.listdir(CACHE_DIR)]
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
    print('cache miss, using GPT3')

    # Add to the cache
    cache_file = os.path.join(CACHE_DIR, str(uuid4()))
    with open(cache_file, 'w') as f:
        f.write(prompt + separator + result)

    return result


def get_db_schema_text(db_name: str) -> str:
    """
    Get the schema of an SQL query.

    """

    return str(subprocess.check_output(['sqlite3', db_name, '.schema']), 'utf-8')


def english2sql(english_query: str, schema_text: Optional[str] = None, use_cache: bool = True) -> str:
    """
    Convert a query written in english to an SQL query.

    """

    # generate an English sentence describing the schema
    if schema_text:
        tables = parse_schema(schema_text)
        created_tables = [t for t in tables if 'sqlite_sequence' not in t['table_name']]
        if len(created_tables) == 0:
            raise ValueError('Error: there are no tables')
        db_spec = 'The database contains '
        for table_idx, table in enumerate(created_tables):
            table_name = table['table_name']
            db_spec += 'a "' + table_name + '" table with the fields '
            for field_idx, field in enumerate(table['fields']):
                name = field['name']
                type = field['type']
                if name == 'id':
                    continue
                db_spec += name + ' (' + type_hint2schema_type(type) + ')';
                if field_idx < len(table['fields'])-1:
                    db_spec += ', '
            db_spec += '; '
        # always add this example table for GPT3
        db_spec += 'and an "apples" table with the fields name (VARCHAR), weight (INTEGER), is_green (BOOLEAN).'

        prompt = (
            f'Turn the following English sentences into valid SQLite statements. {db_spec}\n'
            f'\n'
            f'English: get all of the apples\n'
            f'SQL: SELECT * FROM apples;\n'
            f'\n'
            f'English: get an apple\'s name by its id\n'
            f'SQL: SELECT name FROM apples WHERE id = ?;\n'
            f'\n'
            f'English: create a new apple that is not green\n'
            f'SQL: INSERT INTO apples (name, weight, is_green) VALUES (?, ?, false);\n'
            f'\n'
            f'English: {english_query.strip()}\n'
            f'SQL:'
        )

    else:
        prompt = (
            f'Turn the following English sentences into valid SQLite statements.\n'
            f'\n'
            f'English: {english_query.strip()}\n'
            f'SQL:'
        )

    response = cached_gpt3(prompt, use_cache=use_cache).strip()
    return response


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

    def valid_char(c: str) -> bool:
        return c.isalnum() or c == ' ' or c == '_'

    result = cached_gpt3(prompt, use_cache=use_cache)
    result = ''.join(c for c in result if valid_char(c))
    while len(result) > 0 and result[0].isnumeric():
        result = result[1:]
    if len(result) == 0:
        result = 'untitled'
    return '_'.join(result.strip().lower().split(' '))


def generate_endpoint(endpoint: Endpoint, schema_text: str, use_cache=True) -> str:
    """
    Generate a FastAPI endpoint from an SQL query.

    short_name: a name for the query in snake_case
    sql_query: an SQL query

    """

    sql_query = english2sql(endpoint.value, schema_text, use_cache=use_cache)
    func_name = english2summary_name(endpoint.value)
    inputs, outputs = parse_query(sql_query, schema_text)

    template = '''
<<<RESPONSE_CLASS>>>

@app.<<<METHOD>>>("<<<URL>>>", response_model=<<<RESPONSE_MODEL>>>)
async def <<<FUNC_NAME>>>(<<<PARAMS>>>) -> <<<RESPONSE_MODEL>>>:
    \'\'\'
    <<<ENGLISH_QUERY>>>
    \'\'\'
    cur = con.cursor()
    cur.execute('<<<SQL_QUERY>>>', <<<BINDINGS>>>)
    res: List[Any] = []
    output_names: List[str] = <<<OUTPUT_NAME_LIST>>>
    for row in cur.fetchall():
        row_dict = dict()
        for k, v in zip(output_names, row):
            row_dict[k] = v
        res.append(row_dict)
    con.commit()
    <<<RETURN_STATEMENT>>>
    '''

    params = ', '.join(f'{c["name"]}: {c["type"]}' for c in inputs)
    if len(inputs) > 0:
        bindings = '(' + ', '.join(c["name"] for c in inputs) + ',)'
    else:
        bindings = ''
    output_name_list = '[' + ', '.join([f'\'{c["name"]}\'' for c in outputs]) + ']'

    if len(outputs) > 0:
        response_model = f'List[OutputType_{func_name}]'
        return_statement = 'return res'
        response_class = \
            f'class OutputType_{func_name}(BaseModel):\n' + \
            '    ' + '\n    '.join(f'{c["name"]}: {c["type"]}' for c in outputs)
    else:
        response_model = 'None'
        return_statement = 'return None'
        response_class = ''

    template = template.replace('<<<FUNC_NAME>>>', func_name)
    template = template.replace('<<<URL>>>', endpoint.url)
    template = template.replace('<<<METHOD>>>', endpoint.method.lower())
    template = template.replace('<<<SQL_QUERY>>>', sql_query)
    template = template.replace('<<<PARAMS>>>', params)
    template = template.replace('<<<ENGLISH_QUERY>>>', endpoint.value)
    template = template.replace('<<<BINDINGS>>>', bindings)
    template = template.replace('<<<OUTPUT_NAME_LIST>>>', output_name_list)
    template = template.replace('<<<RESPONSE_MODEL>>>', response_model)
    template = template.replace('<<<RETURN_STATEMENT>>>', return_statement)
    template = template.replace('<<<RESPONSE_CLASS>>>', response_class)
    return template


def generate_app(title: str, endpoints: List[Endpoint], use_cache: bool = True):

    code = '''
from typing import List, Union, Literal, Optional, Dict, Any
from fastapi import FastAPI, Path, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sqlite3

app = FastAPI(
    title="<<<TITLE>>>",
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

con = sqlite3.connect('<<<DB_NAME>>>')

    '''

    schema_text = get_db_schema_text(DB_NAME)

    code = code.replace('<<<TITLE>>>', title)
    code = code.replace('<<<DB_NAME>>>', DB_NAME)

    for endpoint in endpoints:
        endpoint_code = generate_endpoint(endpoint, schema_text)
        code += endpoint_code

    return code


def read_plain_txt(input_fn: str) -> Tuple[List[str], List[str]]:
    """
    Parses the input_fn and returns a tuple of two lists of strings,
    holding the migrations and queries respectively.

    Formally,
    (
        [
            <english str>,
            ...
        ],
        [
            <english str>,
            ...
        ]
    )

    """

    with open(input_fn, 'r') as f:
        migrations = []
        queries = []
        mode = 'none'
        for line in f:
            stripped = line.strip()
            if len(stripped) == 0:
                continue
            if stripped.lower() == '== migrations':
                if mode != 'none':
                    raise ValueError(f'Invalid {input_fn}: The migrations section should appear first.')
                mode = 'migrations'
            elif stripped.lower() == '== queries':
                if mode != 'migrations':
                    raise ValueError(f'Invalid {input_fn}: The queries section should appear after the migrations section.')
                mode = 'queries'
            elif stripped[0] == '#':
                pass
            else:
                if mode == 'migrations':
                    migrations.append(stripped)
                elif mode == 'queries':
                    queries.append(stripped)
                else:
                    pass
        return migrations, queries


def run_necessary_migrations(sql_migrations: List[str], english_migrations: List[str]):
    """
    Given a list of all SQL migrations (can be any valid SQLite statements),
    this function either determines that the given migrations are invalid
    because old ones have been modified, or applies the new migrations.

    Note: The given list should contain all migrations, not just new ones.
          This function will check the English version, not the sql version.
    """


    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    cur.execute('''
        SELECT name FROM sqlite_master WHERE type='table' AND name = '__plainapi_migrations';
    ''')
    rows = cur.fetchall()
    existing_migrations: List[Any] = []
    if len(rows) == 0:
        # create the table
        cur.execute('''
            CREATE TABLE __plainapi_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                sql_query VARCHAR(500) NOT NULL, 
                english_query VARCHAR(500) NOT NULL
            );
        ''')
    else:
        cur.execute('''
            SELECT sql_query, english_query FROM __plainapi_migrations ORDER BY id ASC;
        ''')
        for sql_query, english_query in cur.fetchall():
            existing_migrations.append({'sql': sql_query, 'english': english_query})

    # ensure the existing migrations are correct
    for a, b in zip(existing_migrations, english_migrations):
        if a['english'] != b:
            raise ValueError(f'Invalid previously applied migration (it has been changed):\n  "{a["english"]}" -> "{b}"')

    if len(sql_migrations) != len(english_migrations):
        raise ValueError('Internal: There are more SQL migrations than original English migrations')

    if len(existing_migrations) < len(sql_migrations):
        print('Running migrations...')
        for idx, (sql, english) in enumerate(zip(sql_migrations, english_migrations)):
            if idx < len(existing_migrations):
                pass
            else:
                print(f'  ...{english}')
                cur.execute(sql)
                cur.execute('''
                    INSERT INTO __plainapi_migrations (sql_query, english_query) VALUES (?, ?);
                ''', (sql, english,))
        print('All up to date.')
    else:
        print('No migrations to run.')

    con.commit()


# def generate_app_old(input_fn: str = 'plain.txt', output_fn: str = 'api.py', use_cache: bool = True):
#     """
#     Given a file of English sentences, output a file containing a FastAPI web server.

#     """

#     english_migrations, english_queries = read_plain_txt(input_fn)
#     print('Migrations:')
#     for english_migration in english_migrations:
#         print(f' -> {english_migration}')
#     print('Queries:')
#     for english_query in english_queries:
#         print(f' -> {english_query}')

#     sql_migrations = [english2sql(m, use_cache=use_cache) for m in english_migrations]
#     run_necessary_migrations(sql_migrations, english_migrations)

#     code = generate_app_from_english_queries('My API', english_queries)
#     with open(output_fn, 'w') as f:
#         f.write(code)

#     command_to_run = 'uvicorn ' + output_fn.split('.')[0] + ':app'
#     print(f'Successfully created API! Try running `{command_to_run}`')


# if __name__ == '__main__':
#     with open('migrations.txt', 'r') as f:
#         english_migrations = [m.strip() for m in f.read().split('\n\n')]
#     sql_migrations = [english2sql(m) for m in english_migrations]
#     run_necessary_migrations(sql_migrations, english_migrations)

