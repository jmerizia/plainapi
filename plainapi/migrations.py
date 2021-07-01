import sqlite3


def run_necessary_migrations(db_name: str, sql_migrations: list[str], english_migrations: list[str]):
    """
    Given a list of all SQL migrations (can be any valid SQLite statements),
    this function either determines that the given migrations are invalid
    because old ones have been modified, or applies the new migrations.

    Note: The given list should contain all migrations, not just new ones.
          This function will check the English version, not the sql version.
    """


    con = sqlite3.connect(db_name)
    cur = con.cursor()

    cur.execute('''
        SELECT name FROM sqlite_master WHERE type='table' AND name = '__plainapi_migrations';
    ''')
    rows = cur.fetchall()
    existing_migrations = []
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
