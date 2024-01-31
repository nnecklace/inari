from compiler.tokenizer import Token
from compiler.ast import Expression, BinaryOp, Literal, Identifier, IfThenElse

def peek(tokens: list[Token]) -> Token:
    if tokens:
        return tokens[-1]
    else:
        return Token(location=-1, type='end', text='')

def pop_expected(tokens: list[Token], expected: str | list[str] | None = None) -> Token:
    if peek(tokens).type == 'end':
        raise Exception(f'Expected a token, all tokens have been consumed')
        
    token = tokens.pop()

    if isinstance(expected, str) and token.text != expected:
        raise Exception(f'{token.location}: expected "{expected}"')
    if isinstance(expected, list) and token.text not in expected:
        comma_separated = ", ".join([f'"{e}"' for e in expected])
        raise Exception(f'{token.location}: expected one of: {comma_separated}')

    return token

def parse_int_literal(tokens: list[Token]) -> Literal:
    if peek(tokens).type != 'int_literal':
        raise Exception(f'{peek(tokens).location}: expected an integer literal')
    token = pop_expected(tokens)
    return Literal(int(token.text))

def parse_identifier(tokens: list[Token]) -> Identifier:
    if peek(tokens).type != 'identifier':
        raise Exception(f'{peek(tokens).location}: expected an identifier')
    token = pop_expected(tokens)
    return Identifier(token.text)

def parse_if_then_else(tokens: list[Token]) -> Expression:
    pop_expected(tokens, 'if')
    cond = parse_expression(tokens)
    pop_expected(tokens, 'then')
    then = parse_expression(tokens)

    if_then_else = IfThenElse(cond=cond, then=then)

    if peek(tokens).text == 'else':
        pop_expected(tokens, 'else')
        if_then_else.otherwise = parse_expression(tokens)

    return if_then_else

def parse_factor(tokens: list[Token]) -> Expression:
    if peek(tokens).text == '(':
        return parse_parenthesized(tokens)
    elif peek(tokens).type == 'int_literal':
        return parse_int_literal(tokens)
    elif peek(tokens).type == 'identifier':
        if peek(tokens).text == 'if':
            return parse_if_then_else(tokens)
        else:
            return parse_identifier(tokens)
    else:
        raise Exception(f'{peek(tokens).location}: expected an integer literal or an identifier')

def parse_parenthesized(tokens: list[Token]) -> Expression:
    pop_expected(tokens, '(')
    expr = parse_expression(tokens)
    pop_expected(tokens, ')')
    return expr

def parse_term(tokens: list[Token]) -> Expression:
    left = parse_factor(tokens)

    while peek(tokens).text in ['*', '/']:
        left = BinaryOp(
            left,
            pop_expected(tokens).text, # operator
            parse_factor(tokens) # right term
        )

    return left

def parse_expression(tokens: list[Token]) -> BinaryOp:
    left = parse_term(tokens)

    while peek(tokens).text in ['+', '-']:
        left = BinaryOp(
            left,
            pop_expected(tokens).text, # operator
            parse_term(tokens) # right term
        )
    
    return left

def parse(tokens: list[Token]) -> Expression:
    tokens.reverse()
    expr = parse_expression(tokens)

    if tokens:
        raise Exception(f'Unparsable exception, tokens left unparsed {tokens}')

    return expr