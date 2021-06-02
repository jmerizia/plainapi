from pglast import parse_sql
from typing import Literal


def identify_type(sql) -> Literal['SELECT', 'CREATE', 'UPDATE', 'ALTER']:
    root = parse_sql(sql)
    if len(root) > 1:
        raise ValueError('Expected just one SQL statement')
    if len(root) == 0:
        raise ValueError('Received no SQL statements')
    stmt = root[0]
    print(len(stmt.items()))
    # assert isinstance(stmt, ast.RawStmt)
    # select_stmt = stmt.stmt
    # assert isinstance(select_stmt, ast.SelectStmt)

identify_type('select * from users where id = ?')