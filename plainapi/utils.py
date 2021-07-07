import subprocess


def get_db_schema_text(db_name: str) -> str:
    return str(subprocess.check_output(['sqlite3', db_name, '.schema']), 'utf-8')


def text2valid_id(text: str) -> str:
    clean = ''.join(c if c.isalnum() else ' ' for c in text)
    parts = [s.strip() for s in clean.split(' ') if s.strip() != '']
    combined = '_'.join(parts)
    if combined[0].isnumeric():
        combined = 'func_' + combined
    return combined
