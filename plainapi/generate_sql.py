from typing import List, Tuple

from plainapi.types import Context
from plainapi.gpt3 import cached_complete
from plainapi.parse_sql import parse_schema, parse_outputs


def expand_columns(sql: str, schema_text: str) -> str:
    """
    In the case that the * operator is used in SQL, this will expand the query to include all columns in the schema.
    Note: This does not support sub-queries.
    """
    if '*' in sql:
        explicit_column_names = []
        outputs = parse_outputs(sql, schema_text)
        schema = parse_schema(schema_text)
        for output in outputs:
            left, right = output.split('.')
            if right.strip() == '*':
                pass
        columns = [c['name'] for c in schema['columns']]
        sql = sql.replace('*', ','.join(columns))
    schema = parse_schema(schema_text)


def english2sql(english_query: str, context: Context, schema_text: str) -> Tuple[str, List[str]]:

    # TODO: use context

    prompt = \
f"""
Turn the following English sentences into valid SQLite statements, along with the input parameters. Here's the database schema:

{schema_text}

The first three examples will be about a table called "apples" with id, name, weight, and is_green, but the rest should refer to the above schema.

English: get all of the apples
SQL: SELECT * FROM apples; params = []

English: get an apple\'s name by its id
SQL: SELECT name FROM apples WHERE id = ?; params = [id]

English: create a new apple that is not green with name {{name}} and weight {{weight}}
SQL: INSERT INTO apples (name, weight, is_green) VALUES (?, ?, false); params = [name, weight]

English: {english_query.strip()}
SQL:"""

    response = cached_complete(prompt, engine='davinci')
    sql, params = response.split(';')
    _, array = params.split('=')
    variable_names = [variable.strip() for variable in array.strip()[1:-1].split(',')]
    print(english_query, '->', sql, variable_names)
    return sql, variable_names
