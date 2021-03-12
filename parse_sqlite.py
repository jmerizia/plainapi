# Partial implementation of parsing SQLite language:
# For full specification see https://sqlite.org/syntax/select-stmt.html

from enum import Enum
import pprint
import time


def perror(msg):
    print("Error:", msg)
    quit()

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
            perror(f'tokenize_sql() :: Invalid character \'{text[r]}\'')


def consume_token(tokens, idx):
    if idx == len(tokens):
        return None, idx
    else:
        return tokens[idx], idx + 1


def schema_type2type_hint(schema_type_text):
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
        perror('Expected at least one token in schema type')
    if tok == 'VARCHAR':
        return 'str'
    elif tok == 'INTEGER':
        return 'int'
    elif tok == 'BOOLEAN':
        return 'bool'
    else:
        perror('Invalid type')


def get_columns_for_table(schema_text, table_name):
    tables_text = [s.strip() for s in schema_text.split(';')]
    for text in tables_text:
        table_name_from_schema = text.split(' ')[2].strip()
        if table_name_from_schema == table_name:
            table_fields_text = ' '.join(text.split(' ')[3:])[1:-1].split(',')
            table_fields_text = [s.strip() for s in table_fields_text]
            table_fields_text = [s for s in table_fields_text if len(s) > 0]
            break
    fields = []
    for text in table_fields_text:
        tokens = text.split(' ')
        name = tokens[0]
        type = tokens[1]
        attributes = ' '.join(tokens[2:])
        fields.append({
            'name': name,
            'type': schema_type2type_hint(type)
        })
    return fields


def get_select_stmt_output_type(select_text, schema_text):
    """
    An SQL parser that parses an SQL schema (string) and an SQL query (string)
    into a list of dicts representing the input and output types respectively.

    A bit more formally:
    (
        # inputs:
        [
            {
                'name': <str>,
                'type': <str>
            },
            ...
        ],
        # outputs:
        [
            {
                'name': <str>,
                'type': <str>,
            },
            ...
        ]
    )

    """
    # TODO: This implementation is just the bare minimum to get
    #       this to work. This should eventually be expanded to a full SQL parser.

    tokens = list(tokenize_sql(select_text))
    idx = 0
    tok, idx = consume_token(tokens, idx)
    if not tok:
        perror('Expected statement')
    elif tok.upper() != 'SELECT':
        perror(f'Invalid token \'{tok}\'to start SELECT statement')
    tok, idx = consume_token(tokens, idx)
    if not tok:
        perror('Expected token after SELECT')
    if tok == '*':
        all_columns = True
        column_names = []
    else:
        all_columns = False
        column_names = [tok]
        while True:
            tok, idx = consume_token(tokens, idx)
            if not tok:
                break
            elif tok == ',':
                tok, idx = consume_token(tokens, idx)
                if not tok:
                    perror('Expected token after \',\' token')
                column_names.append(tok)
            else:
                idx -= 1
                break
    tok, idx = consume_token(tokens, idx)
    if not tok or tok.upper() != 'FROM':
        perror('Expected FROM token after column names in SELECT statement')
    tok, idx = consume_token(tokens, idx)
    if not tok:
        perror('Expected table name after FROM in SELECT statement')
    table_name = tok
    schema_columns = get_columns_for_table(schema_text, table_name)
    # filter the columns we want
    if all_columns:
        chosen_columns = schema_columns
    else:
        chosen_columns = []
        for name in column_names:
            schema_column = [c for c in schema_columns if c['name'] == name]
            if len(schema_column) == 0:
                perror(f'No such column \'{name}\' in the schema')
            else:
                chosen_columns.append(schema_column[0])

    # Now, parse inputs (VERY rudimentary)
    num_inputs = select_text.count('?')
    # TODO: we should probably at least get the names of the inputs...
    input_types = [{'name': f'in{i}', 'type': 'str'} for i in range(1, num_inputs+1)]
    return input_types, chosen_columns


if __name__ == '__main__':
    queries = [
        """
        SELECT * FROM users;
        """,
        """
        SELECT email, nickname FROM users WHERE id = ?;
        """,
    ]

    schema_text = """
        CREATE TABLE users (
            id INTEGER NOT NULL,
            email VARCHAR(200) NOT NULL,
            nickname VARCHAR(200) NOT NULL,
            score INTEGER NOT NULL,
            is_admin BOOLEAN NOT NULL
        );
        CREATE TABLE tweets (
            id INTEGER NOT NULL,
            name VARCHAR(200) NOT NULL,
            points INTEGER NOT NULL,
            claimed_by INTEGER
        );
    """

    pp = pprint.PrettyPrinter(indent=4)
    for query in queries:
        print(f'Query: {query}')
        res = get_select_stmt_output_type(query, schema_text)
        pp.pprint(res)

