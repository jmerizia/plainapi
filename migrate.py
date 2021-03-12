import sqlite3

schema = '''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    email VARCHAR(200) NOT NULL, 
    name VARCHAR(200) NOT NULL, 
    age INTEGER NOT NULL, 
    location VARCHAR(200) NOT NULL,
    is_admin BOOLEAN NOT NULL 
);
CREATE TABLE tweets (
    id INTEGER NOT NULL, 
    text VARCHAR(200) NOT NULL, 
    created INTEGER NOT NULL
);
'''

con = sqlite3.connect('demo.db')
cur = con.cursor()
for table_schema in schema.split(';'):
    cur.execute(table_schema)

cur.execute('''INSERT INTO users (email, name, age, location, is_admin)
               VALUES ('321+1@vt.edu', 'Jake1', 22, 'United States', true)''')

cur.execute('''INSERT INTO users (email, name, age, location, is_admin)
               VALUES ('321+2@vt.edu', 'Jake2', 42, 'United States', false)''')

cur.execute('''INSERT INTO users (email, name, age, location, is_admin)
               VALUES ('321+3@vt.edu', 'Jake3', 32, 'Canada', false)''')

con.commit()
