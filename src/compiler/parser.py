from compiler.tokenizer import Token
from compiler.ast import Expression, BinaryOp, Literal, Identifier, IfThenElse, FuncCall, UnaryOp, While, Var, Block

left_associative_binary_operators = [
    ['*', '/', '%'],
    ['+', '-'],
    ['<', '<=', '>', '>='],
    ['==', '!='],
    ['and'],
    ['or']
]

def peek(tokens: list[Token]) -> Token:
    if tokens:
        return tokens[-1]
    else:
        return Token(location=-1, type='end', text='')

def pop_next(tokens: list[Token], expected: str | None = None) -> Token:
    if peek(tokens).type == 'end':
        raise Exception(f'Expected a token, all tokens have been consumed')
        
    token = tokens.pop()

    if isinstance(expected, str) and token.text != expected:
        raise Exception(f'{token.location}: expected "{expected}"')

    return token

def parse_bool_literal(tokens: list[Token]) -> Literal:
    next = pop_next(tokens).text
    if next.lower() == 'true':
        return Literal(True)

    if next.lower() == 'false':
        return Literal(False)

    raise Exception(f'Expected either true or false, got {next}')

def parse_int_literal(tokens: list[Token]) -> Literal:
    return Literal(int(pop_next(tokens).text))

def parse_identifier(tokens: list[Token]) -> Identifier:
    return Identifier(pop_next(tokens).text)

def parse_if_then_else(tokens: list[Token]) -> Expression:
    pop_next(tokens, 'if')
    cond = parse_block_or_expression(tokens)

    pop_next(tokens, 'then')
    then = parse_block_or_expression(tokens)

    if_then_else = IfThenElse(cond=cond, then=then)

    if isinstance(then, Block) and peek(tokens).text == ';':
        pop_next(tokens, ';')
    elif peek(tokens).text == 'else':
        pop_next(tokens, 'else')
        if_then_else.otherwise = parse_block_or_expression(tokens)
        if isinstance(if_then_else.otherwise, Block) and peek(tokens).text == ';':
            pop_next(tokens, ';')

    return if_then_else

def parse_unary_op(tokens: list[Token]) -> Expression:
    return UnaryOp(
        op=pop_next(tokens).text,
        right=parse_expression(tokens)
    )

def parse_while(tokens: list[Token]) -> Expression:
    pop_next(tokens, 'while')
    condition = parse_block_or_expression(tokens)
    pop_next(tokens, 'do')
    body = parse_block_or_expression(tokens)

    if isinstance(body, Block) and peek(tokens).text == ';':
        pop_next(tokens,';')

    return While(
        cond=condition,
        body=body
    )

# check if needed
def parse_vars(tokens: list[Token]) -> Block | Var:
    var = parse_var(tokens)

    if peek(tokens).text == ';':
        pop_next(tokens, ';')
        block = Block([])
        block.statements.append(var)
        semi_colon_count = 1
        while peek(tokens).text == 'var' and peek(tokens).type != 'end':
            block.statements.append(parse_var(tokens))
            if peek(tokens).text == ';':
                pop_next(tokens, ';')
                semi_colon_count += 1

        if semi_colon_count == len(block.statements):
            block.statements.append(Literal(None))

        return block

    return var

def parse_var(tokens: list[Token]) -> Var:
    pop_next(tokens, 'var')
    identifier = parse_factor(tokens)
    following = peek(tokens)
    if not isinstance(identifier, Identifier):
        raise Exception(f'{following.location}: expected an identifier got {following.type}')

    initialization = None

    if peek(tokens).text == '=':
        pop_next(tokens, '=')
        initialization = parse_expression(tokens)

    following = peek(tokens)

    if following.text != ';' and following.type != 'end' and following.text != '}':
        raise Exception(f'Expected ; after var declaration instead found {following.text}')

    return Var(
        name=identifier,
        initialization=initialization
    )

def ended_with_block(expr: Expression) -> bool:
    if isinstance(expr, IfThenElse):
        if expr.otherwise and isinstance(expr.otherwise, Block):
            return True
        if expr.then and isinstance(expr.then, Block):
            return True

    if isinstance(expr, While) and isinstance(expr.body, Block):
        return True

    return False

def ended_with_semi_colon(expr: Expression) -> bool:
    if isinstance(expr, IfThenElse):
        if expr.otherwise and isinstance(expr.otherwise, Block) and expr.otherwise.ended_with_semi_colon:
            return True
        if expr.then and isinstance(expr.then, Block) and expr.then.ended_with_semi_colon:
            return True

    if isinstance(expr, While) and isinstance(expr.body, Block) and expr.body.ended_with_semi_colon:
        return True

    return False


def parse_block(tokens: list[Token], top_level_block: bool = False) -> Expression:
    match_closing_bracket = False

    if peek(tokens).text == '{':
        match_closing_bracket = True
        pop_next(tokens, '{')

    semi_colon_count = 0
    statements = []
    while peek(tokens).text != '}' and peek(tokens).type != 'end':
        if peek(tokens).text == '{':
            statements.append(parse_block(tokens))
            if peek(tokens).text == ';':
                pop_next(tokens, ';')
                semi_colon_count += 1
            if peek(tokens).text == '}':
                break
            else:
                semi_colon_count += 1
        else:
            statements.append(parse_expression(tokens))

            if ended_with_block(statements[-1]):
                semi_colon_count += 1
            elif peek(tokens).text == ';':
                pop_next(tokens, ';')
                semi_colon_count += 1
            else:
                break

    if match_closing_bracket:
        pop_next(tokens, '}')

    if semi_colon_count == len(statements):
        if len(statements) == 0 or not ended_with_block(statements[-1]):
            statements.append(Literal(None))
        elif ended_with_block(statements[-1]) and ended_with_semi_colon(statements[-1]):
            statements.append(Literal(None))

    if top_level_block and len(statements) == 1:
        return statements[0]

    return Block(statements=statements, ended_with_semi_colon=(peek(tokens).text == ';'))

def parse_factor(tokens: list[Token]) -> Expression:
    text = peek(tokens).text
    token_type = peek(tokens).type
    if text == '(':
        return parse_parenthesized(tokens)
    elif text == '{':
        return parse_block(tokens)
    elif token_type == 'int_literal':
        return parse_int_literal(tokens)
    elif token_type == 'bool_literal':
        return parse_bool_literal(tokens)
    elif token_type == 'identifier':
        if text == 'if':
            return parse_if_then_else(tokens)
        elif text == 'while':
            return parse_while(tokens)
        elif text == 'var':
            return parse_var(tokens)
        elif text  == 'not':
            return parse_unary_op(tokens)
        else:
            return parse_identifier(tokens)
    elif token_type == 'operator' and text == '-':
        return parse_unary_op(tokens)
    else:
        raise Exception(f'{peek(tokens).location}: expected an integer literal or an identifier')

def parse_parenthesized(tokens: list[Token]) -> Expression:
    pop_next(tokens, '(')
    expr = parse_expression(tokens)
    pop_next(tokens, ')')
    return expr

def parse_function_call(identifier: Identifier, tokens: list[Token]) -> FuncCall:
    args = []
    pop_next(tokens, '(')
    while peek(tokens).text != ')':
        if peek(tokens).meta == 'end' or peek(tokens).type == 'end':
            raise Exception(f'{peek(tokens).location}: expected )')
        args.append(parse_expression(tokens))
        if peek(tokens).text == ',':
            pop_next(tokens)
    pop_next(tokens, ')')

    return FuncCall(name=identifier.name, args=args)

def parse_binary_operation(tokens: list[Token], operators: list[str], left: Expression) -> Expression:
    curr_precedence = left_associative_binary_operators.index(operators)

    while peek(tokens).text in operators:
        op = pop_next(tokens).text # operator
        right = parse_factor(tokens) # right term

        for indx, ops in enumerate(left_associative_binary_operators):
            if peek(tokens).text in ops and indx < curr_precedence:
                right = parse_binary_operation(tokens, ops, right)
                break

        left = BinaryOp(
            left,
            op,
            right
        )

    return left

def parse_expression(tokens: list[Token]) -> Expression:
    left = parse_factor(tokens)

    if isinstance(left, Identifier) and peek(tokens).text == '(':
        return parse_function_call(left, tokens)

    for operator in left_associative_binary_operators:
        left = parse_binary_operation(tokens, operator, left)

    if peek(tokens).text == '=':
        op = pop_next(tokens).text # operator
        right = parse_expression(tokens) # right term

        if isinstance(right, Block) and peek(tokens).text == ';':
            pop_next(tokens, ';')

        return BinaryOp(
            left,
            op,
            right
        )

    return left

def parse_block_or_expression(tokens: list[Token]) -> Expression:
    if peek(tokens).text == '{':
        return parse_block(tokens)
    else:
        return parse_expression(tokens)

def parse(tokens: list[Token]) -> Expression:
    tokens.reverse()
    root = parse_block(tokens, True)

    if tokens:
        raise Exception(f'Unparsable exception, tokens left unparsed {tokens}')

    return root
