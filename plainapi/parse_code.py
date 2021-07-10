from typing import Literal, Optional, Tuple, List, TypedDict, Union, Dict, Any, cast
import itertools
import json

from plainapi.gpt3 import cached_complete
from plainapi.generate_sql import english2sql
from plainapi.utils import get_db_schema_text


class Variable(TypedDict):
    name: str
    type: str

class Function(TypedDict):
    name: str
    inputs: List[Variable]
    outputs: List[Variable]

class Context(TypedDict):
    variables: List[Variable]

class Interval(TypedDict):
    left: int
    right: int

class FunctionCallStatement(TypedDict):
    type: Literal['function_call']
    context: Context
    function_name: str
    inputs: List[Variable]
    outputs: List[Variable]

class IfStatement(TypedDict):
    type: Literal['if']
    context: Context
    condition: str
    case_true: 'CodeBlock'
    case_false: Optional['CodeBlock']

class ExceptionStatement(TypedDict):
    type: Literal['exception']
    code: Optional[int]
    message: Optional[str]

class AssignmentStatement(TypedDict):
    type: Literal['assignment']
    name: str
    value: str

class PythonStatement(TypedDict):
    type: Literal['python']
    original: str
    code: str

class SQLStatement(TypedDict):
    type: Literal['sql']
    original: str
    sql: str

class OutputStatement(TypedDict):
    type: Literal['output']
    value: str

Statement = Union[
    IfStatement,
    FunctionCallStatement,
    ExceptionStatement,
    AssignmentStatement,
    PythonStatement,
    SQLStatement,
    OutputStatement,
]

CodeBlock = List[Statement]


def determine_code_block_type(first_line: str) -> Literal['if', 'exception', 'assignment', 'output', 'something-else']:
    first_line = first_line.strip()

    if first_line.startswith('if'):
        return 'if'

    prompt = \
f"""For each of the following statements, determine what kind of statement it would be if written in code. All statements must be one of the following:
"exception"
"assignment"
"output"
"something-else"

Note: If you're confused, just put something-else

Statement: user <- get a user with email {{email}}
Type: assignment
Reason: the left arrow

Statement: let "apples" be all the applies that are red
Type: assignment
Reason: the initial "let"

Statement: report 400 "Forbidden"
Type: exception
Reason: the word "report" and the negative sounding message

Statement: raise that This action is not allowed
Type: exception
Reason: the word "raise"

Statement: return the email of the user with id {{id}}
Type: output
Reason: the word "return" at the beginning

Statement: output {{user}}
Type: output
Reason: the word "output"

Statement: send verification email to {{email}} with {{nickname}}
Type: something-else
Reason: this is better handled with a function call, not an exception, assignment, or output.

Statement: {first_line.strip()}
Type:"""

    result = cached_complete(prompt, engine='curie').strip()
    if result == 'exception' or result == 'assignment' or result == 'output' or result == 'something-else':
        return result
    else:
        raise ValueError('Internal Error: failed to match')


def match_function_call(code_string: str, available_functions: list[Function]) -> Union[str, None]:
    """ Returns either the code to execute a matching function call or None if there's no match. """

    code_string = code_string.strip()

    functions_string = ''
    for f in available_functions:
        name = f['name']
        inputs_string = ', '.join(i['name'] + ': ' + i['type'] for i in f['inputs'])
        outputs_string = ', '.join(o['type'] for o in f['outputs'])
        function_string = f'{name}({inputs_string}) -> ({outputs_string})'
        functions_string += function_string + '\n'

    prompt = \
f"""Given the following list of functions, either turn each of the statements into a Python function call or put "n/a". You must only use the given functions.

Functions:
launch_spaceship(destination: str) -> None
{functions_string}

statement: send a space ship out to Mars
function name: launch_spaceship("Mars")

statement: pass the salt
function name: n/a

statement: {code_string.strip()}
function name:"""

    result = cached_complete(prompt, engine='curie').strip()
    first_paren_idx = result.find('(')
    if first_paren_idx == -1:
        raise ValueError(f'Internal Error: invalid function call {result}')
    name = result[:first_paren_idx]
    if name in [f['name'] for f in available_functions]:
        return result
    elif result == 'n/a':
        return None
    else:
        raise ValueError('Internal Error: function name is not among the given names')


def determine_else_or_elif(text: str) -> Tuple[Literal['else', 'elif', 'n/a'], Optional[str]]:

    prompt = \
f"""Determine if the following statements represent an "if" block, a terminal "else" code block, or an "else-if" code block. If it's an else block, put "else", if it's an if, put "if:" followed by the condition itself, and if it's an else-if, put "else-if: " followed by the condition. If neither of these make sense, put "n/a".

Statement: else
Type: else

Statement: otherwise, if the current user is not logged in
Type: else-if: the current user is not logged in

Statement: otherwise
Type: else

Statement: go to the moon
Type: n/a

Statement: if {{password}} is not a good password
Type: if: {{password}} is not a good password

Statement: report something
Type: n/a

Statement: {text.strip()}
Type:"""

    result = cached_complete(prompt, engine='curie').strip()
    if result == 'else':
        return 'else', None
    elif result.startswith('else-if'):
        parts = result.split(':')
        assert len(parts) == 2
        condition = parts[1].strip()
        return 'elif', condition
    else:
        return 'n/a', None


def count_leading_spaces(text: str) -> int:
    cnt = 0
    for c in text:
        if c == ' ':
            cnt += 1
        else:
            break
    return cnt


def parse_exception(text: str) -> ExceptionStatement:
    pass

    prompt = \
f"""The following statements represent exception statements. Parse them into form "code=<code>, message=<message>". If the code or message are not present, put "None" for that value.

Statement: report 400: "Forbidden"
Parsed: code=400, message="Forbidden"

Statement: report "Bad password"
Parsed: code=None, message="Bad password"

Statement: raise 100
Parsed: code=100, message=None

Statement: throw "Not enough data", 500
Parsed: code=500, message="Not enough data"

Statement: {text.strip()}
Parsed:"""

    result = cached_complete(prompt, engine='curie')
    parts = result.split(',')
    assert len(parts) == 2
    code_parts = parts[0].split('=')
    message_parts = parts[1].split('=')
    assert len(code_parts) == 2
    assert len(message_parts) == 2
    assert code_parts[0].strip() == 'code'
    assert message_parts[0].strip() == 'message'
    code_str = code_parts[1].strip()
    code = int(code_str) if code_str != 'None' else None
    return ExceptionStatement(
        type='exception',
        code=code,
        message=message_parts[1].strip()
    )


def parse_assignment(text: str) -> AssignmentStatement:

    prompt = \
f"""Each of the following statements represent assignment statements. For each, parse out the name of the variable from the value statement as a json.

Description: hashed password <- hash {{password}}
Parsed: {{"name": "hashed password", "value": "hash {{password}}"}}

Description: let oldest user be the oldest user in the database
Parsed: {{"name": "oldest user", "value": "the oldest user in the database"}}

Description: Assign "last post" to the most recent post
Parsed: {{"name": "last post", "value": "the most recent post"}}

Description: user <- get a user with name equal to "Jake"
Parsed: {{"name": "user", "value": "get a user with name equal to \"Jake\""}}

Description: {text.strip()}
Parsed:"""

    result = cached_complete(prompt, engine='curie')
    parsed = json.loads(result)
    name = parsed['name']
    value = parsed['value']
    return AssignmentStatement(
        type='assignment',
        name=name,
        value=value
    )


def parse_python_or_sql_statement(text: str, schema_text: str) -> Union[PythonStatement, SQLStatement]:

    prompt = \
"""Convert each of the following statements into one line of Python code. If it is better suited by an SQL statement, just put "sql".
Note: in the current context, the following variables already exist:
users: List[User]
i: int
j: int

where,
User is a TypedDict with fields "id": int, "email": str, and "joined": datetime.

Statement: take the sum of i and j
Python: sum(i, j)

Statement: if i is greater than j
Python: i > j

Statement: sort the users by id
Python: list(sorted(users, key=lambda u: u["id"]))

Statement: get the emails of all the users
Python: sql

Statement: if the product of i and j exceeds the number of users
Python: i * j > len(users)

Statement: {text}
Python:"""

    result = cached_complete(prompt, engine='curie').strip()
    if result == 'sql':
        sql = english2sql(english_query=text, schema_text=schema_text)
        return SQLStatement(
            type='sql',
            original=text,
            sql=sql
        )
    else:
        return PythonStatement(
            type='python',
            original=text,
            code=result
        )


def parse_output(text: str) -> OutputStatement:

    prompt = \
f"""For the following statements, parse out what should be returned.

Statement: output the oldest user
Output: the oldest user

Statement: return {{user}}
Output: {{user}}

Statement: {text.strip()}
Output:"""

    result = cached_complete(prompt, engine='curie')
    stat = OutputStatement(
        type='output',
        value=result.strip()
    )
    return stat


def _parse_code_block(lines: List[str], context: Context, schema_text: str, global_line_offset: int, local_line_index: int, should_indent: bool) -> Tuple[CodeBlock, Context, int]:
    assert local_line_index < len(lines)
    original_indent = count_leading_spaces(lines[local_line_index])
    prev_line = lines[local_line_index - 1]
    prev_indent = count_leading_spaces(prev_line)
    if should_indent and prev_indent >= original_indent:
        raise ValueError(f'Expected indented block on line {global_line_offset + local_line_index}.')

    block: CodeBlock = []
    while local_line_index < len(lines):
        current_indent = count_leading_spaces(lines[local_line_index])
        if current_indent < original_indent:
            break
        line_type = determine_code_block_type(lines[local_line_index])
        if line_type == 'if':
            condition = lines[local_line_index][2:].strip()
            if local_line_index == len(lines) - 1:
                raise ValueError('Expected indented code block after "if" statement.')
            case_true_block, context, local_line_index = _parse_code_block(
                lines=lines,
                context=context,
                schema_text=schema_text,
                global_line_offset=global_line_offset,
                local_line_index=local_line_index + 1,
                should_indent=True
            )
            # check if we reached the end
            if local_line_index >= len(lines):
                stat = IfStatement(
                    type='if',
                    context=context,
                    condition=condition,
                    case_true=case_true_block,
                    case_false=None
                )
                block.append(stat)
            else:
                # at this point, we have climbed out of any children of the if statement true case
                indent = count_leading_spaces(lines[local_line_index])
                if original_indent != indent:
                    raise ValueError(f'Expected indent of else block on line {global_line_offset + local_line_index} to match original indent.')
                next_statement_type, next_condition = determine_else_or_elif(lines[local_line_index])
                if next_statement_type == 'else':
                    if local_line_index == len(lines) - 1:
                        raise ValueError('Expected indented block after "else" statement.')
                    case_false_block, context, local_line_index = _parse_code_block(
                        lines=lines,
                        context=context,
                        schema_text=schema_text,
                        global_line_offset=global_line_offset,
                        local_line_index=local_line_index + 1,
                        should_indent=True
                    )
                    stat = IfStatement(
                        type='if',
                        context=context,
                        condition=condition,
                        case_true=case_true_block,
                        case_false=case_false_block
                    )
                    block.append(stat)
                elif next_statement_type == 'elif':
                    # TODO: implement else-if chains (leaving it out for now to reduce complexity)
                    print(lines[local_line_index])
                    raise ValueError('else-if chains are not implemented yet!')
                else:
                    stat = IfStatement(
                        type='if',
                        context=context,
                        condition=condition,
                        case_true=case_true_block,
                        case_false=None
                    )
                    block.append(stat)

        elif line_type == 'exception':
            exception_stat = parse_exception(lines[local_line_index])
            block.append(exception_stat)

        elif line_type == 'assignment':
            assignment_stat = parse_assignment(lines[local_line_index])
            block.append(assignment_stat)

        elif line_type == 'output':
            output_stat = parse_output(lines[local_line_index])
            block.append(output_stat)

        elif line_type == 'something-else':
            raise ValueError('TODO')

        else:
            raise ValueError(f'Invalid statement on line {global_line_offset + local_line_index}')
    
        local_line_index += 1

    return block, context, local_line_index


def parse_code_block(lines: List[str], context: Context, schema_text: str, global_line_offset: int) -> CodeBlock:
    assert len(lines) > 0
    block, context, local_line_index = _parse_code_block(
        lines=lines,
        context=context,
        schema_text=schema_text,
        global_line_offset=global_line_offset,
        local_line_index=0,
        should_indent=False
    )
    return block
