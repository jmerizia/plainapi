from enum import Enum


def perror(msg):
    print("Error:", msg)
    quit()

def tokenize_sql(text):
    l = 0
    r = 0
    special_tokens = [
        '<>', '<=', '>=', '=', '<', '>', '!=',
        '(', ')', ';', '+', '-', '*', '/', '\'',
        '.',
    ]

    while r < len(text):

        # skip whitespace
        while r < len(text) and text[r].isspace():
            r += 1

        # EOF
        if r >= len(text):
            pass

        # word token
        elif text[r].isalpha():
            l = r
            r += 1
            while r < len(text) and text[r].isalnum():
                r += 1
            yield text[l:r]

        # number token
        elif text[r].isnumeric() and text[r] != '0':
            l = r
            r += 1
            while r < len(text) and text[r].isnumeric():
                r += 1
            yield text[l:r]

        # special token
        elif any(text[r:].startswith(tok) for tok in special_tokens):
            l = r
            for tok in special_tokens:
                if text[r:].startswith(tok):
                    r = l + len(tok)
                    yield text[l:r]
                    break
        
        else:
            perror("Invalid token at TODO")

class NodeKind(Enum):
    Select = 'Select'
    SelectExpression = 'SelectExpression'
    Token = 'Token'
    TableExpression = 'TableExpression'
    Name = 'Name'
    Expression = 'Expression'
    AndCondition = 'AndCondition'
    Condition = 'Condition'
    Boolean = 'Boolean'
    Int = 'Int'
    Decimal = 'Decimal'
    Number = 'Number'
    Numeric = 'Numeric'
    Value = 'Value'
    Term = 'Term'
    Factor = 'Factor'
    Summand = 'Summand'
    Operand = 'Operand'
    Long = 'Long'
    ColumnRef = 'ColumnRef'
    Compare = 'Compare'

class Node:
    def __init__(self, name, kind, children=None):
        self.name = name
        self.kind = kind
        if children is None:
            self.children = []
        else:
            self.children = children

def consume_token(tokens, idx):
    if idx == len(tokens):
        return None, idx
    else:
        return tokens[idx], idx + 1

def parse_quoted_name(tokens, idx):
    print('TODO implement quoted name')
    return None, idx

def parse_name(tokens, idx):
    child, idx = parse_quoted_name(tokens, idx)
    if child:
        return child
    else:
        tok, idx = consume_token(tokens, idx)
        if not tok:
            perror("Expected token")
        elif not (tok[0].isalpha() or tok[0] == '_'):
            idx -= 1
            return None, idx
        else:
            for c in tok[1:]:
                if not (c.isalnum() or c == '_'):
                    idx -= 1
                    return None, idx
                else:
                    pass
            node = Node(name=tok, kind=NodeKind.Name)
            return node, idx

def parse_null(tokens, idx):
    tok, idx = consume_token(tokens, idx)
    if not tok:
        return None, idx
    elif tok.upper() == 'NULL':
        node = Node(name=tok, kind=NodeKind.Null)
        return node, idx
    else:
        idx -= 1
        return None, idx

def parse_boolean(tokens, idx):
    tok, idx = consume_token(tokens, idx)
    if not tok:
        return None, idx
    elif tok.upper() in ['TRUE', 'FALSE']:
        node = Node(name=tok, kind=NodeKind.Boolean)
        return node, idx
    else:
        idx -= 1
        return None, idx

def parse_number(tokens, idx):
    tok, idx = consume_token(tokens, idx)
    if not tok:
        return None, idx
    elif tok.isnumeric():
        node = Node(name=tok, kind=NodeKind.Number)
        return node, idx
    else:
        idx -= 1
        return None, idx

def parse_decimal(tokens, idx):
    tok, idx = consume_token(tokens, idx)
    node = Node(name='', kind=NodeKind.Decimal)
    if tok == '-':
        child = Node(name=tok, kind=NodeKind.Token)
        node.children.append(child)
        multiplier = -1
    else:
        idx -= 1
        multiplier = 1
    child, idx = parse_number(tokens, idx)
    if child:
        node.children.append(child)
        tok, idx = consume_token(tokens, idx)
        if not tok:
            pass
        elif tok == '.':
            child = Node(name=tok, kind=NodeKind.Token)
            node.children.append(child)
            child, idx = parse_number(tokens, idx)
            if child:
                node.children.append(child)
            else:
                perror("Expected number following . in decimal")
        else:
            idx -= 1
        return node, idx
    else:
        return None, idx

def parse_long(tokens, idx):
    tok, idx = consume_token(tokens, idx)
    node = Node(name='', kind=NodeKind.Long)
    if tok == '-':
        child = Node(name=tok, kind=NodeKind.Token)
        node.children.append(child)
        multiplier = -1
    else:
        idx -= 1
        multiplier = 1
    child, idx = parse_number(tokens, idx)
    if child and -9223372036854775808 <= multiplier * int(child.name) <= 9223372036854775807:
        node.children.append(child)
        return node, idx
    else:
        return None, idx

def parse_int(tokens, idx):
    tok, idx = consume_token(tokens, idx)
    node = Node(name='', kind=NodeKind.Int)
    if tok == '-':
        child = Node(name=tok, kind=NodeKind.Token)
        node.children.append(child)
        multiplier = -1
    else:
        idx -= 1
        multiplier = 1
    child, idx = parse_number(tokens, idx)
    if child and -2147483648 <= multiplier * int(child.name) <= 2147483647:
        node.children.append(child)
        return node, idx
    else:
        return None, idx

def parse_numeric(tokens, idx):
    child, idx = parse_int(tokens, idx)
    if child:
        node = Node(name='', kind=NodeKind.Numeric)
        node.children.append(child)
        return node, idx
    else:
        child, idx = parse_long(tokens, idx)
        if child:
            node = Node(name='', kind=NodeKind.Numeric)
            node.children.append(child)
            return node, idx
        else:
            child, idx = parse_decimal(tokens, idx)
            if child:
                node = Node(name='', kind=NodeKind.Numeric)
                node.children.append(child)
                return node, idx
            else:
                return None, idx

def parse_string(tokens, idx):
    tok, idx = consume_token(tokens, idx)
    if tok[0] == '\'' and tok[-1] == '\'':
        node = Node(name=tok, kind=NodeKind.String)
        return node, idx
    else:
        idx -= 1
        return None, idx

def parse_value(tokens, idx):
    child, idx = parse_string(tokens, idx)
    node = Node(name='', kind=NodeKind.Value)
    if child:
        node.children.append(child)
        return node, idx
    else:
        child, idx = parse_numeric(tokens, idx)
        if child:
            node.children.append(child)
            return node, idx
        else:
            child, idx = parse_boolean(tokens, idx)
            if child:
                node.children.append(child)
                return node, idx
            else:
                child, idx = parse_null(tokens, idx)
                if child:
                    node.children.append(child)
                    return node, idx
                else:
                    return None, idx
    return None, idx

def parse_column_ref(tokens, idx):
    child, idx = parse_name(tokens, idx)
    node = Node(name='', kind=NodeKind.ColumnRef)
    if child:
        # TODO
        print('TODO: family name')
        node.children.append(child)
        return node, idx
    else:
        return None, idx

def parse_term(tokens, idx):
    child, idx = parse_value(tokens, idx)
    node = Node(name='', kind=NodeKind.Term)
    if child:
        node.children.append(child)
        return node, idx
    else:
        print('TODO term: there are a lot of other cases that have not been implemented')
        child, idx = parse_column_ref(tokens, idx)
        if child:
            node.children.append(child)
            return node, idx
        else:
            print('TODO term: there are a lot of other cases that have not been implemented')
            return None, idx

def parse_factor(tokens, idx):
    child, idx = parse_term(tokens, idx)
    if child:
        node = Node(name='', kind=NodeKind.Factor)
        node.children.append(child)
        while True:
            tok, idx = consume_token(tokens, idx)
            if not tok:
                return node, idx
            elif tok in ['*', '/']:
                child = Node(name=tok, kind=NodeKind.Token)
                node.children.append(child)
                child, idx = parse_term(tokens, idx)
                if child:
                    node.children.append(child)
                else:
                    perror('Expected factor after + or - token')
            else:
                idx -= 1
                return node, idx
    else:
        return None, idx

def parse_summand(tokens, idx):
    child, idx = parse_factor(tokens, idx)
    if child:
        node = Node(name='', kind=NodeKind.Summand)
        node.children.append(child)
        while True:
            tok, idx = consume_token(tokens, idx)
            if not tok:
                return node, idx
            elif tok in ['+', '-']:
                child = Node(name=tok, kind=NodeKind.Token)
                node.children.append(child)
                child, idx = parse_factor(tokens, idx)
                if child:
                    node.children.append(child)
                else:
                    perror('Expected factor after + or - token')
            else:
                idx -= 1
                return node, idx
    else:
        return None, idx

def parse_operand(tokens, idx):
    child, idx = parse_summand(tokens, idx)
    if child:
        node = Node(name='', kind=NodeKind.Operand)
        node.children.append(child)
        while True:
            tok, idx = consume_token(tokens, idx)
            if not tok:
                return node, idx
            elif tok == '||':
                child = Node(name=tok, kind=NodeKind.Token)
                node.children.append(child)
                child, idx = parse_summand(tokens, idx)
                if child:
                    node.children.append(child)
                else:
                    perror('Expected summand after ||')
            else:
                idx -= 1
                return node, idx
    else:
        return None, idx

def parse_compare(tokens, idx):
    compare_tokens = ['<>', '<=', '>=', '=', '<', '>', '!=']
    tok, idx = consume_token(tokens, idx)
    if tok in compare_tokens:
        node = Node(name=tok, kind=NodeKind.Compare)
        return node, idx
    else:
        idx -= 1
        return None, idx

def parse_condition(tokens, idx):
    child, idx = parse_operand(tokens, idx)
    if child:
        node = Node(name='', kind=NodeKind.Condition)
        node.children.append(child)
        child, idx = parse_compare(tokens, idx)
        if child:
            node.children.append(child)
            child, idx = parse_operand(tokens, idx)
            if child:
                node.children.append(child)
                return node, idx
            else:
                perror('Expected operand after compare')
        else:
            tok, idx = consume_token(tokens, idx)
            if not tok:
                print('TODO!') # TODO
            elif tok.upper() == 'IN':
                print('TODO!') # TODO
            elif tok.upper() == 'LIKE':
                print('TODO!') # TODO
            elif tok.upper() == 'BETWEEN':
                print('TODO!') # TODO
            elif tok.upper() == 'IS':
                print('TODO!') # TODO
            elif tok.upper() == 'NOT':
                print('TODO!') # TODO
            else:
                perror('Expected one of IN, LIKE, BETWEEN, IS, or NOT after operand')
        return node, idx
    else:
        tok, idx = consume_token(tokens, idx)
        if not tok:
            return None, idx
        elif tok.upper() == 'NOT':
            child = Node(name='NOT', kind=NodeKind.Token)
            node.children.append(child)
            child, idx = parse_expression(tokens, idx)
            if child:
                node.children.append(child)
                return node, idx
            else:
                perror("Expected expression after NOT")
        elif tok == '(':
            child, idx = parse_expression(tokens, idx)
            if child:
                node.children.append(child)
                tok, idx = consume_token(tokens, idx)
                if tok == ')':
                    child = Node(name=tok, kind=NodeKind.Token)
                    node.children.append(child)
                    return node, idx
                else:
                    perror("Expected closing paren after expression")
            else:
                perror('Expected expression after \'(\'.')
        else:
            idx -= 1
            return None, idx

def parse_and_condition(tokens, idx):
    child, idx = parse_condition(tokens, idx)
    if not child:
        return None, idx
    else:
        node = Node(name='', kind=NodeKind.AndCondition)
        node.children.append(child)
        while True:
            tok, idx = consume_token(tokens, idx)
            if not tok:
                return node, idx
            elif tok.upper() == 'AND':
                child, idx = parse_condition(tokens, idx)
                if child:
                    node.children.append(child)
                else:
                    perror("Expected condition")
            else:
                return node, idx

def parse_expression(tokens, idx):
    child, idx = parse_and_condition(tokens, idx)
    if child:
        node = Node(name='', kind=NodeKind.Expression)
        node.children.append(child)
        while True:
            tok, idx = consume_token(tokens, idx)
            if not tok:
                return node, idx
            elif tok.upper() == 'OR':
                child, idx = parse_and_condition(tokens, idx)
                if child:
                    node.children.append(child)
                else:
                    perror("Expected and_condition")
            else:
                idx -= 1
                return node, idx
    else:
        return None, idx

def parse_table_expression(tokens, idx):
    node = Node(name='', kind=NodeKind.TableExpression)
    child, idx = parse_name(tokens, idx)
    print('TODO: there are some more cases to check here')
    # TODO
    if child:
        node.children.append(child)
        return node, idx
    else:
        return None, idx

def parse_select(tokens, idx):
    tok = tokens[idx]
    idx += 1
    if tok.upper() != 'SELECT':
        idx -= 1
        return None, idx
    node = Node(name='SELECT', kind=NodeKind.Select)
    print('TODO parse hint') # TODO
    tok, idx = consume_token(tokens, idx)
    if not tok:
        perror("Expected token")
    if tok.upper() == 'DISTINCT':
        child = Node(name='DISTINCT', kind=NodeKind.Token)
        node.children.append(child)
    elif tok.upper() == 'ALL':
        child = Node(name='ALL', kind=NodeKind.Token)
        node.children.append(child)
    else:
        idx -= 1
    tok, idx = consume_token(tokens, idx)
    if not tok:
        perror("Expected token")
    if tok == '*':
        child = Node(name='*', kind=NodeKind.Token)
        node.children.append(child)
    elif tok == '(':
        child = Node(name='(', kind=NodeKind.Token)
        node.children.append(child)
        print('TODO: some more logic needed here')
    else:
        idx -= 1
        #child, idx = parse_term(tokens, idx)
        #print('TODO')
    tok, idx = consume_token(tokens, idx)
    if not tok:
        perror("Expected token")
    # TODO: potential repeats
    if tok.upper() == 'FROM':
        child = Node(name='FROM', kind=NodeKind.Token)
        node.children.append(child)
        child, idx = parse_table_expression(tokens, idx)
        if child:
            node.children.append(child)
        else:
            perror("Expected table expression")
    else:
        perror("Expected FROM token")
    # TODO: optional column def
    tok, idx = consume_token(tokens, idx)
    if not tok:
        pass
    else:
        if tok.upper() == 'WHERE':
            child = Node(name='token', kind=NodeKind.Token)
            child, idx = parse_expression(tokens, idx)
            if child:
                node.children.append(child)
            else:
                perror("Expected expression following WHERE token")
        else:
            idx -= 1
    return node, idx
    
def print_tree(node, depth=0):
    if depth > 10:
        return
    print('|  '*depth, end='')
    print(f'"{node.name}", {node.kind}')
    for child in node.children:
        print_tree(child, depth+1)

text = """
SELECT * FROM users WHERE id = 10
"""

print("Query:", text.strip())
tokens = list(tokenize_sql(text))
print('Tokens:', tokens)
tree, _ = parse_select(tokens, 0)
if tree:
    print_tree(tree)
else:
    print('Failed to parse')

