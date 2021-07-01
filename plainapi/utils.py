import subprocess


def get_db_schema_text(db_name: str) -> str:
    return str(subprocess.check_output(['sqlite3', db_name, '.schema']), 'utf-8')
