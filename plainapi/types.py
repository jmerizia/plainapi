from typing import Tuple, List, TypedDict, Union, Dict, Any, Literal, Optional


class Input(TypedDict):
    name: str
    type: str


class Column(TypedDict):
    name: str
    type: str


class Table(TypedDict):
    name: str
    columns: list[Column]


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
    function_name: str
    inputs: List[Variable]
    outputs: List[Variable]
    original: str


class ExceptionStatement(TypedDict):
    type: Literal['exception']
    code: Optional[int]
    message: Optional[str]
    original: str


class PythonConditionalStatement(TypedDict):
    type: Literal['python-conditional']
    original: str
    code: str


class PythonStatement(TypedDict):
    type: Literal['python']
    original: str
    code: str
    return_type: str


class IfStatement(TypedDict):
    type: Literal['if']
    condition: PythonConditionalStatement
    case_true: 'CodeBlock'
    case_false: Optional['CodeBlock']


class SQLStatement(TypedDict):
    type: Literal['sql']
    original: str
    sql: str
    inputs: List[Variable]
    outputs: List[Variable]


RightHandSideStatement = Union[PythonStatement, SQLStatement, FunctionCallStatement]


class AssignmentStatement(TypedDict):
    type: Literal['assignment']
    name: str
    value: RightHandSideStatement
    original: str


class OutputStatement(TypedDict):
    type: Literal['output']
    value: RightHandSideStatement
    original: str


Statement = Union[
    IfStatement,
    FunctionCallStatement,
    ExceptionStatement,
    AssignmentStatement,
    PythonStatement,
    PythonConditionalStatement,
    SQLStatement,
    OutputStatement,
]


CodeBlock = List[Statement]


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
    implementation: CodeBlock

