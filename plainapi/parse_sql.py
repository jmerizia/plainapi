from typing import Tuple, List, TypedDict, Union, Dict, Any, cast

from plainapi.gpt3 import cached_complete


class Input(TypedDict):
    name: str
    type: str


class Column(TypedDict):
    name: str
    type: str


class Table(TypedDict):
    name: str
    columns: list[Column]


def tokenize_sql(text):
    l = 0
    r = 0
    special_tokens = [
        '<>', '<=', '>=', '=', '<', '>', '!=',
        '(', ')', ';', '+', '-', '*', '/', '\'',
        '.', ',', '?',
    ]

    while r < len(text):

        # skip whitespace
        while r < len(text) and text[r].isspace():
            r += 1

        # EOF
        if r >= len(text):
            pass

        # word token
        elif text[r].isalpha() or text[r] == '_':
            l = r
            r += 1
            while r < len(text) and (text[r].isalnum() or text[r] == '_'):
                r += 1
            yield text[l:r]

        # number token
        elif text[r].isnumeric():
            l = r
            r += 1
            while r < len(text) and text[r].isnumeric():
                r += 1
            yield text[l:r]

        # special token
        elif any(text[r:].startswith(tok) for tok in special_tokens):
            l = r
            for tok in special_tokens:
                if text[r:].startswith(tok):
                    r = l + len(tok)
                    yield text[l:r]
                    break

        else:
            raise ValueError(f'Invalid query: {text}\n  tokenize_sql() :: Invalid character \'{text[r]}\'')


def consume_token(tokens, idx):
    if idx == len(tokens):
        return None, idx
    else:
        return tokens[idx], idx + 1


def schema_type2type_hint(schema_type_text: str):
    """
    Map an SQLite type (from a schema) to a Python type hint.

    VARCHAR(200) -> str
    INTEGER -> int
    BOOLEAN -> bool

    """

    tokens = list(tokenize_sql(schema_type_text))
    idx = 0
    tok, idx = consume_token(tokens, idx)
    if not tok:
        raise ValueError('Expected at least one token in schema type')
    low = tok.lower()
    if low.startswith('varchar'):
        return 'str'
    elif low == 'text':
        return 'str'
    elif low == 'integer':
        return 'int'
    elif low == 'boolean':
        return 'bool'
    else:
        raise ValueError(f'Invalid type "{tok}"')


def type_hint2schema_type(type_hint: str):
    """
    Map a Python type hint to an SQLite schema type.

    str -> VARCHAR(200)
    int -> INTEGER
    bool -> BOOLEAN

    """

    if type_hint == 'str':
        return 'VARCHAR'
    elif type_hint == 'int':
        return 'INTEGER'
    elif type_hint == 'bool':
        return 'BOOLEAN'
    else:
        raise ValueError(f'Invalid type "{type_hint}"')


def parse_outputs(sql: str) -> list[str]:
    """
    Given a single SQL statement, return a list of output columns of the SQL statement.
    All output columns are returned in the format "table_name.column_name".
    If the * is used, then the format will be "table_name.*".
    """

    prompt = \
f"""Determine the output columns of the following Postgres SQL statements, with each column formatted as "table_name.column_name".

SQL: SELECT users.id, posts.value FROM users INNER JOIN posts ON posts.user_id = user.id WHERE posts.created_at > ?;
Columns: users.id, posts.value

SQL: SELECT * FROM users;
Columns: users.*

SQL: SELECT value FROM posts;
Columns: posts.value

SQL: select email from users where id = ? and is_admin  = true;
Columns: users.email

SQL: {sql.strip()}
Columns:"""

    result = cached_complete(prompt, engine='curie').strip()
    columns = [s.strip() for s in result.split(',')]
    return columns


def parse_schema(schema_text: str) -> list[Table]:
    """
    An SQL parser that takes a database schema and return all the parsed tables.
    """

    tables_text = [s.strip() for s in schema_text.strip().split(';')]
    tables_text = [s for s in tables_text if len(s) > 0]
    tables: list[Table] = []
    for text in tables_text:
        if 'IF NOT EXISTS' in text:
            # TODO: handle this case
            continue
        table_name = text.split(' ')[2].strip()
        table_fields_text = ' '.join(text.split(' ')[3:])[1:-1].split(',')
        table_fields_text = [s.strip() for s in table_fields_text]
        table_fields_text = [s for s in table_fields_text if len(s) > 0]
        columns: list[Column] = []
        for text in table_fields_text:
            if text.startswith('FOREIGN'):
                # this is a foreign key constraint
                continue
            tokens = text.split(' ')
            name = tokens[0]
            type = tokens[1]
            attributes = ' '.join(tokens[2:])
            columns.append({
                'name': name,
                'type': schema_type2type_hint(type)
            })
        tables.append({'name': table_name, 'columns': columns})
    return tables


def parse_inputs(sql: str, schema_text: str) -> list[str]:

    qms = sql.count('?')
    if qms == 0:
        question = 'What is the type of the \'?\' variable?'
    else:
        question = f'What are the types of the {qms} \'?\' variables?'

    prompt = \
f"""Given the following SQL query, determine the types of the inputs. Here is the schema of the database:

{schema_text}

SQL: SELECT * FROM users WHERE id = ?;
Q: What is the type of the '?' variable?
A: integer

SQL: INSERT INTO users (name, email, age, is_admin) VALUES (?, ?, ?, ?);
Q: What are the types of the four '?' values?
A: string, string, integer, boolean

SQL: {sql}
Q: {question}
A:"""

    result = cached_complete(prompt, engine='curie')
    types = [s.strip() for s in result.split(',')]
    return types


def get_columns_for_table(schema_text: str, table_name: str) -> Any:
    tables = parse_schema(schema_text)
    res = [table for table in tables if table['name'] == table_name]
    if len(res) != 1:
        raise ValueError(f'Invalid table name {table_name}')
    return res[0]['columns']
