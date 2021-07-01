from typing import Literal, Tuple, List, TypedDict, Union, Dict, Any, cast

from plainapi.gpt3 import cached_complete


class Header(TypedDict):
    method: Literal['GET', 'POST', 'PATCH', 'DELETE']
    url: str


class FunctionInput(TypedDict):
    name: str
    type: str


class FunctionOutput(TypedDict):
    name: str
    type: str


class FunctionTypeDefinition(TypedDict):
    inputs: list[FunctionInput]
    outputs: list[FunctionOutput]


class Endpoint(TypedDict):
    header: Header
    requirements: FunctionTypeDefinition
    implementation: str


def parse_header(header_string: str) -> Header:

    if '\n' in header_string:
        raise ValueError('Expected header string to be one line.')

    prompt = \
f"""For each of the following sentences describing HTTP endpoints, determine the method and url. Valid methods are GET, POST, PATCH, and DELETE.

description: GET at url /users/with-email/{{email}}
method, url: GET /users/with-email/{{email}}

description: post at url /users/signup
method and url: POST /users/signup

description: {header_string.strip()}
method and url:"""

    result = cached_complete(prompt, engine='curie').strip()
    method_url = [s.strip() for s in result.split(' ')]
    if len(method_url) != 2:
        raise ValueError(f'Internal Error: Unexpected number of arguments in header: {result}')
    method, url = method_url
    method = method.upper()
    if method == 'GET' or method == 'POST' or method == 'PATCH' or method == 'DELETE':
        return {
            'method': method,
            'url': url
        }
    else:
        raise ValueError(f'Invalid method {method}')


def parse_requirements(requirements_string: str) -> FunctionTypeDefinition:

    if '\n' in requirements_string:
        raise ValueError('Expected requirements string to be one line.')

    prompt = \
f"""For each of the following sentences describing a programming function, determine the input parameters and output types, where types are valid Python types.
Note: "auth" is a special variable of type "Any".

description: * requires auth *
function stub: (auth: Any) -> ()

description: requires email, password. returns number and a string
function stub: (email: str, password: str) -> (int, str)

description: * requires authentication and an id (string)
function stub: (auth: Any, id: str) -> ()

description: {requirements_string.strip()}
function stub:"""

    inputs: list[FunctionInput] = []
    outputs: list[FunctionOutput] = []

    result = cached_complete(prompt, engine='curie').strip()
    inputs_string, outputs_string = [s.strip() for s in result.split('->')]
    input_strings = [s.strip() for s in inputs_string[1:-1].split(',')]
    output_strings = [s.strip() for s in outputs_string[1:-1].split(',')]
    for input in input_strings:
        name, type = [s.strip() for s in input.split(':')]
        inputs.append({
            'name': name,
            'type': type,
        })
    for output in output_strings:
        outputs.append({
            'name': 'unknown',
            'type': output
        })
    return {
        'inputs': inputs,
        'outputs': outputs,
    }


def parse_endpoint(endpoint_string: str, schema_text: str) -> Endpoint:
    lines = endpoint_string.split('\n')
    if len(lines) < 3:
        raise ValueError('Expected endpoint to be at least 3 lines long (header, requirements, and implementation)')
    header_string = lines[0]
    requirements_string = lines[1]
    implementation_string = '\n'.join(lines[2:])
    header = parse_header(header_string)
    requirements = parse_requirements(requirements_string)
    return {
        'header': header,
        'requirements': requirements,
        'implementation': implementation_string
    }
