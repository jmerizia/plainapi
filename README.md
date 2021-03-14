# PlainAPI

This is a tool that lets you create APIs using English language.
It uses GPT3 to translate between user defined queries and SQL statements.

Note: You will need to be in the OpenAI API Beta program in order to use this.

## Installation

Create a file called `.env` and put your OpenAI api key in it with this format:

```
OPENAI_KEY="sk-..."
```

Then, install everything in the `requirements.txt` file.
You might want to use a virtual environment:

```
python3.8 -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
```

Note: This has been tested in Python 3.8, but it _should_ technically work in Python 3.6+
(you might have to play with dependency versions).

## Generate an API

Start by tweaking the `plain.txt` file to modify the migrations and queries
(each query/migration on it's own line).
At the moment, queries can only be as complicated as a single SQL
statement, but this restriction will eventually be lifted.

Then, run the generation script `generate_api.py`.
This will show you all of the queries and generate
a new file called `api.py`.

Once that finishes, you can run your server with `uvicorn api:app`,
and view the OpenAPI docs at [http://localhost:8000/docs](http://localhost:8000/docs).

Enjoy, and please don't hesitate to report errors!

