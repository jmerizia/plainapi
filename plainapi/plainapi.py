from typing import Optional
import os
from dotenv import load_dotenv
import configparser
import argparse

from plainapi.utils import get_db_schema_text
from plainapi.generate_python import generate_app
from plainapi.parse_application import parse_application


def main():
    parser = argparse.ArgumentParser(description='Generate web APIs with plain English.')
    parser.add_argument('command', choices=['init', 'gen', 'start', 'restart'], help='Base command')
    settings_filename = 'plain.ini'
    args = parser.parse_args()

    if args.command == 'gen':

        if not os.path.exists(settings_filename):
            raise ValueError(f'Could not find settings file: {settings_filename}')

        config = configparser.ConfigParser()
        config.read(settings_filename)

        def read_setting(name: str) -> Optional[str]:
            settings = config['default']
            if name in settings:
                return settings[name]
            return None

        endpoints_filename = read_setting('endpoints_filename') or 'endpoints.plain'
        migrations_filename = read_setting('migrations_filename') or 'migrations.plain'
        functions_filename = read_setting('functions_filename') or 'functions.plain'
        target_filename = read_setting('target_filename') or 'app.py'
        db_name = read_setting('db_name') or 'my-app.sqlite3'
        host = read_setting('host') or 'localhost'
        port = read_setting('port') or '3000'
        port = int(port)

        if not os.path.exists(endpoints_filename):
            raise ValueError(f'Could not find endpoints file: {endpoints_filename}')
        if not os.path.exists(migrations_filename):
            raise ValueError(f'Could not find migrations file: {migrations_filename}')
        if not os.path.exists(functions_filename):
            raise ValueError(f'Could not find functions file: {functions_filename}')

        with open(endpoints_filename, 'r') as f:
            endpoints_code = f.read()
        with open(migrations_filename, 'r') as f:
            migrations_code = f.read()
        with open(functions_filename, 'r') as f:
            functions_code = f.read()
        
        schema_text = get_db_schema_text(db_name)
        application = parse_application(endpoints_code=endpoints_code,
                                        functions_code=functions_code,
                                        schema_text=schema_text)

        code = generate_app(application=application,
                            schema_text=schema_text,
                            db_name=db_name,
                            host=host,
                            port=port)
        
        with open(target_filename, 'w') as f:
            f.write(code)

    else:
        raise ValueError(f'Command \'{args.command}\' is not implemented yet!')

if __name__ == '__main__':
    main()
