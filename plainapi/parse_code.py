from typing import Literal, Optional, Tuple, List, TypedDict, Union, Dict, Any, cast
import itertools

from plainapi.gpt3 import cached_complete


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

Statement = Union[IfStatement, FunctionCallStatement, ExceptionStatement]

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
f"""Determine if the following statements represent a terminal "else" code block, or an "else-if" code block. If it's an else block, put "else" and if it's an else-if, put "else-if: " followed by the condition itself. If neither of these make sense, put "n/a".

Statement: else
Type: else

Statement: otherwise, if the current user is not logged in
Type: else-if: the current user is not logged in

Statement: otherwise
Type: else

Statement: go to the moon
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
    assert code_parts[0] == 'code'
    assert message_parts[0] == 'message'
    return ExceptionStatement(
        type='exception',
        code=int(code_parts[1]),
        message=message_parts[1]
    )


def parse_code_block(lines: List[str], context: Context, global_line_offset: int = 0, local_line_index: int = 0, prev_indent: int = 0, descend_block: bool = False) -> Tuple[Optional[Statement], Context, int]:
    if local_line_index >= len(lines):
        return None, context, local_line_index
    indent = count_leading_spaces(lines[local_line_index])
    if descend_block:
        if not indent > prev_indent:
            raise ValueError(f'Expected indented block on line {global_line_offset + local_line_index}.')
    else:
        if indent != prev_indent:
            # we are now climbing out of the indentation tree
            return None, context, local_line_index

    code_block_type = determine_code_block_type(lines[local_line_index])
    if code_block_type == 'if':
        original_indent = indent
        condition = lines[local_line_index][2:].strip()
        case_true: CodeBlock = []
        for idx in itertools.count():
            case_true_stat, context, local_line_index = parse_code_block(
                lines=lines,
                context=context,
                global_line_offset=global_line_offset,
                local_line_index=local_line_index + 1,
                prev_indent=indent,
                # only the first block is "descending" (the rest should match indentation)
                descend_block=(idx == 0)
            )
            if case_true_stat is None or local_line_index >= len(lines):
                break
            case_true.append(case_true_stat)
            indent = count_leading_spaces(lines[local_line_index])
        # check if we reached the end
        if local_line_index >= len(lines):
            stat = IfStatement(
                type='if',
                context=context,
                condition=condition,
                case_true=case_true,
                case_false=None
            )
            return stat, context, local_line_index + 1
        else:
            # at this point, we have climbed out of any children of the if statement true case
            indent = count_leading_spaces(lines[local_line_index])
            if original_indent != indent:
                raise ValueError(f'Expected indent of else block on line {global_line_offset + local_line_index} to match original indent.')

            next_statement_type, next_condition = determine_else_or_elif(lines[local_line_index])
            if next_statement_type == 'else':
                case_false: CodeBlock = []
                for idx in itertools.count():
                    case_false_stat, context, local_line_index = parse_code_block(
                        lines=lines,
                        context=context,
                        global_line_offset=global_line_offset,
                        local_line_index=local_line_index + 1,
                        prev_indent=indent,
                        # only the first block is "descending" (the rest should match indentation)
                        descend_block=(idx == 0)
                    )
                    if case_false_stat is None or local_line_index >= len(lines):
                        break
                    case_false.append(case_false_stat)
                    indent = count_leading_spaces(lines[local_line_index])
                stat = IfStatement(
                    type='if',
                    context=context,
                    condition=condition,
                    case_true=case_true,
                    case_false=case_false
                )
                return stat, context, local_line_index + 1
            elif next_statement_type == 'elif':
                # TODO: implement else-if chains (leaving it out for now to reduce complexity)
                raise ValueError('else-if chains are not implemented yet!')
            else:
                stat = IfStatement(
                    type='if',
                    context=context,
                    condition=condition,
                    case_true=case_true,
                    case_false=None
                )
                return stat, context, local_line_index + 1

    elif code_block_type == 'exception':
        exception = parse_exception(lines[local_line_index])
        return exception, context, local_line_index + 1

    elif code_block_type == 'assignment':
        raise ValueError('TODO')

    elif code_block_type == 'something-else':
        raise ValueError('TODO')

    else:
        raise ValueError(f'Invalid statement on line {global_line_offset + local_line_index}')