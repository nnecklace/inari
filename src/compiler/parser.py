from compiler.location import Location
from compiler.tokenizer import Token
from compiler.ast import Expression, BinaryOp, Literal, Identifier, IfThenElse, FuncCall, UnaryOp, While, Var, Block, BreakContinue, Module
from compiler.types import get_type_from_str

def parse(tokens: list[Token]) -> Expression:
    # reverse tokens such that list works as a stack
    tokens.reverse()

    left_associative_binary_operators = [
        ['*', '/', '%'],
        ['+', '-'],
        ['<', '<=', '>', '>='],
        ['==', '!='],
        ['and'],
        ['or']
    ]

    def peek() -> Token:
        if tokens:
            return tokens[-1]
        else:
            return Token(location=Location(file='', line=-1, column=-1), type='end', text='')

    def pop_next(expected: str | None = None) -> Token:
        if peek().type == 'end':
            raise Exception(f'Expected a token, all tokens have been consumed')
            
        token = tokens.pop()

        if isinstance(expected, str) and token.text != expected:
            raise Exception(f'{token.location}: expected "{expected}"')

        return token

    def parse_bool_literal() -> Literal:
        next = pop_next().text
        if next.lower() == 'true':
            return Literal(True)

        if next.lower() == 'false':
            return Literal(False)

        raise Exception(f'Expected either true or false, got {next}')

    def parse_int_literal() -> Literal:
        return Literal(int(pop_next().text))

    def parse_identifier() -> Identifier:
        return Identifier(pop_next().text)

    def parse_break_continue() -> BreakContinue:
        return BreakContinue(pop_next().text)

    def parse_if_then_else() -> Expression:
        pop_next('if')
        cond = parse_block_or_expression()

        pop_next('then')
        then = parse_block_or_expression()

        if_then_else = IfThenElse(cond=cond, then=then)

        if peek().text == 'else':
            pop_next('else')
            if_then_else.otherwise = parse_block_or_expression()

        return if_then_else

    def parse_unary_op() -> Expression:
        return UnaryOp(
            op=pop_next().text,
            right=parse_expression()
        )

    def parse_while() -> Expression:
        pop_next('while')
        condition = parse_block_or_expression()
        pop_next('do')
        body = parse_block_or_expression()

        return While(
            cond=condition,
            body=body
        )

    def parse_var() -> Var:
        pop_next('var')
        identifier = parse_factor()
        following = peek()
        if not isinstance(identifier, Identifier):
            raise Exception(f'{following.location}: expected an identifier got {following.type}')

        initialization = None
        declared_type = None

        if peek().text == ':':
            pop_next(':')
            declared_type = parse_factor()
            if not isinstance(declared_type, Identifier):
                raise Exception(f'Expceted variable {identifier} type to be an identifier')
            declared_type = get_type_from_str(declared_type.name)

        if peek().text == '=':
            pop_next('=')
            initialization = parse_block_or_expression()

        following = peek()

        if following.text != ';' and \
            following.type != 'end' and \
            following.text != '}' and \
            not includes_end_block(initialization) and \
            not isinstance(initialization, Block):
            raise Exception(f'Expected ; after var declaration instead found {following.text}')

        return Var(
            name=identifier,
            initialization=initialization, # type: ignore[arg-type]
            declared_type=declared_type
        )

    def includes_end_block(expr: Expression | None) -> bool:
        match expr:
            case Block():
                return True
            case Var():
                return includes_end_block(expr.initialization)
            case IfThenElse():
                if expr.otherwise:
                    return isinstance(expr.otherwise, Block)
                return isinstance(expr.then, Block)
            case While():
                return isinstance(expr.body, Block)

        return False

    def parse_block() -> Block:
        last_semi_colon = 0
        statements = []
        pop_next('{')
        while peek().text != '}' and peek().type != 'end':
            block_or_expression = parse_block_or_expression()
            statements.append(block_or_expression)
            if peek().text == ';':
                pop_next(';')
                last_semi_colon = len(statements)
            else:
                if includes_end_block(block_or_expression):
                    continue
                else:
                    break
        pop_next('}')

        if last_semi_colon == len(statements):
            statements.append(Literal(None))

        return Block(statements)

    def parse_factor() -> Expression:
        text = peek().text
        token_type = peek().type
        if text == '(':
            return parse_parenthesized()
        elif text == '{':
            return parse_block()
        elif token_type == 'int_literal':
            return parse_int_literal()
        elif token_type == 'bool_literal':
            return parse_bool_literal()
        elif token_type == 'identifier':
            if text == 'if':
                return parse_if_then_else()
            elif text == 'while':
                return parse_while()
            elif text == 'var':
                return parse_var()
            elif text  == 'not':
                return parse_unary_op()
            elif text == 'break' or text == 'continue':
                return parse_break_continue()
            else:
                return parse_identifier()
        elif token_type == 'operator' and text == '-':
            return parse_unary_op()
        else:
            raise Exception(f'{peek().location}: expected an integer literal or an identifier')

    def parse_parenthesized() -> Expression:
        pop_next('(')
        expr = parse_block_or_expression()
        pop_next(')')
        return expr

    def parse_function_call(identifier: Identifier) -> FuncCall:
        args = []
        pop_next('(')
        while peek().text != ')':
            if peek().type == 'end':
                raise Exception(f'{peek().location}: expected )')
            args.append(parse_block_or_expression())

            if isinstance(args[-1], Var):
                raise Exception('Var is only allowed directly inside blocks {} and in top-level expressions')

            if peek().text == ',':
                pop_next()
        pop_next(')')

        return FuncCall(name=identifier.name, args=args)

    def parse_binary_operation(operators: list[str], left: Expression) -> Expression:
        curr_precedence = left_associative_binary_operators.index(operators)

        while peek().text in operators:
            op = pop_next().text # operator
            right = parse_factor() # right term

            for indx, ops in enumerate(left_associative_binary_operators):
                if peek().text in ops and indx < curr_precedence:
                    right = parse_binary_operation(ops, right)
                    break

            left = BinaryOp(
                left,
                op,
                right
            )

        return left

    def parse_expression() -> Expression:
        left = parse_factor()

        if isinstance(left, Identifier) and peek().text == '(':
            return parse_function_call(left)

        for operator in left_associative_binary_operators:
            left = parse_binary_operation(operator, left)

        if peek().text == '=':
            op = pop_next().text # operator
            right = parse_block_or_expression() # right term

            return BinaryOp(
                left,
                op,
                right
            )

        return left

    def parse_block_or_expression() -> Expression:
        if peek().text == '{':
            return parse_block()
        else:
            return parse_expression()

    root = parse_block()

    if tokens:
        raise Exception(f'Unparsable exception, tokens left unparsed {tokens}')

    return Module('main', root.statements)
