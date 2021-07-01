#!/usr/bin/env python

import sys
import fire  # type: ignore

from parse_sql import parse_query, parse_schema
from generate import get_db_schema_text


def generate_queries(queries_fn: str = './queries.sql', output_fn: str = './queries.py'):
    schema_text = get_db_schema_text('./db/plainapi.sqlite3')
    queries = []
    with open(queries_fn, 'r') as f:
        for line in f:
            query = ''
            for i in range(len(line)):
                if i < len(line) - 1 and line[i:i+2] == '--':
                    break
                query += line[i]
            query = query.strip()
            if len(query) > 0:
                queries.append(query)
    for query in queries:
        if not query.startswith('DELETE') and not query.startswith('UPDATE'):
            print(parse_query(query, schema_text=schema_text))


if __name__ == '__main__':
    fire.Fire(generate_queries)