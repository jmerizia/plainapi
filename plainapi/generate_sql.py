from plainapi.gpt3 import cached_complete


def english2sql(english_query: str, schema_text: str) -> str:

    prompt = \
f"""
Turn the following English sentences into valid SQLite statements. Here's the database schema:

{schema_text}

English: get all of the apples
SQL: SELECT * FROM apples;

English: get an apple\'s name by its id
SQL: SELECT name FROM apples WHERE id = ?;

English: create a new apple that is not green
SQL: INSERT INTO apples (name, weight, is_green) VALUES (?, ?, false);

English: {english_query.strip()}
SQL:"""

    response = cached_complete(prompt)
    return response
