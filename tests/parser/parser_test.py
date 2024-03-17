from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.ast import Argument, BreakContinue, Expression, BinaryOp, FuncDef, Literal, Identifier, IfThenElse, FuncCall, UnaryOp, Block, Var, While, Module
from compiler.types import Bool, Int, Pointer, Unit, Unknown

import unittest

def module(expressions: list[Expression] | Expression) -> Module:
    if isinstance(expressions, Expression):
       return Module('main', [expressions])
    
    return Module('main', expressions)

class ParserTest(unittest.TestCase):
    def test_basic_parser(self) -> None:
        assert parse(tokenize('1+2')) == module(BinaryOp(left=Literal(1), op='+', right=Literal(2)))

    def test_parser_with_complicated_expression(self) -> None:
        assert parse(tokenize('(12 + b) * 2 / (2 + 2) * 2')) == module(BinaryOp(
            right=Literal(2), 
            op='*', 
            left=BinaryOp(
                left=BinaryOp(
                    right=Literal(2),
                    op='*',
                    left=BinaryOp(
                        right=Identifier('b'),
                        op='+',
                        left=Literal(12)
                    )
                ),
                op='/',
                right=BinaryOp(
                    left=Literal(2),
                    op='+',
                    right=Literal(2)
                ),
            )
        ))

    def test_parse_from_high_to_low_precedence(self) -> None:
        assert parse(tokenize('b*b+2')) == module(BinaryOp(
            left=BinaryOp(
                left=Identifier('b'),
                op='*',
                right=Identifier('b')
            ),
            op='+',
            right=Literal(2)
        ))

    def test_parse_simple_if(self) -> None:
        assert parse(tokenize('if a then b')) == module(IfThenElse(cond=Identifier(name='a'), then=Identifier(name='b')))

    def test_parse_simple_if_else(self) -> None:
        assert parse(tokenize('if a then b else c')) == module(IfThenElse(cond=Identifier(name='a'), then=Identifier(name='b'), otherwise=Identifier('c')))

    def test_parse_simple_if_arithmetic(self) -> None:
        assert parse(tokenize('if a + 4 then b*b+2 else c-4')) == module(IfThenElse(
            cond=BinaryOp(left=Identifier(name='a'), op='+', right=Literal(4)),
            then=BinaryOp(left=BinaryOp(left=Identifier('b'), op='*', right=Identifier('b')), op='+', right=Literal(2)),
            otherwise=BinaryOp(left=Identifier('c'), op='-', right=Literal(4))
        ))

    def test_parse_if_as_part_of_expression(self) -> None:
        assert parse(tokenize('1 + if true then 2 else 3')) == module(BinaryOp(
            left=Literal(1),
            op='+',
            right=IfThenElse(
                cond=Literal(True),
                then=Literal(2),
                otherwise=Literal(3)
            )
        ))
    
    def test_parse_function_calls_simple(self) -> None:
        assert parse(tokenize('f(x)')) == module(FuncCall(name=Identifier('f'), args=[Identifier('x')]))

    def test_parse_function_calls_multi_args(self) -> None:
        assert parse(tokenize('f(x,y,z)')) == module(FuncCall(name=Identifier('f'), args=[Identifier('x'), Identifier('y'), Identifier('z')]))
    
    def test_parse_function_calls_with_expression(self) -> None:
        assert parse(tokenize('f(x+y)')) == module(FuncCall(name=Identifier('f'), args=[BinaryOp(left=Identifier('x'), op='+', right=Identifier('y'))]))

    def test_parse_function_calls_with_expression_with_parens(self) -> None:
        assert parse(tokenize('f((x+y)+z)')) == module(FuncCall(name=Identifier('f'), args=[BinaryOp(left=BinaryOp(left=Identifier('x'), op='+', right=Identifier('y')), op='+', right=Identifier('z'))]))

    def test_parse_function_calls_with_expression_with_parens2(self) -> None:
        assert parse(tokenize('f((x+y)+z+(y+8))')) == module(FuncCall(name=Identifier('f'), args=[
            BinaryOp(
                right=BinaryOp(
                    left=Identifier('y'), 
                    op='+', 
                    right=Literal(8)
                ), 
                op='+', 
                left=BinaryOp(
                    left=BinaryOp(
                        left=Identifier('x'),
                        op='+',
                        right=Identifier('y')
                    ),
                    op='+',
                    right=Identifier('z')
                ))]
            ))
    
    def test_parse_function_calls_with_many_parens(self) -> None:
        assert parse(tokenize('f((((((((((((((1+1))))))))))))))')) == module(FuncCall(name=Identifier('f'), args=[BinaryOp(left=Literal(1),op='+',right=Literal(1))]))
    
    def test_parse_function_calls_with_nested_function_calls(self) -> None:
        assert parse(tokenize('f(g(x), h(m(n(y))))')) == module(FuncCall(name=Identifier('f'), args=[FuncCall(name=Identifier('g'), args=[Identifier('x')]), FuncCall(name=Identifier('h'),args=[FuncCall(name=Identifier('m'), args=[FuncCall(name=Identifier('n'),args=[Identifier('y')])])])]))

    def test_parse_function_calls_with_nested_function_call_and_expression(self) -> None:
        assert parse(tokenize('f(x, g(x), y+x)')) == module(FuncCall(name=Identifier('f'), args=[Identifier('x'), FuncCall(name=Identifier('g'), args=[Identifier('x')]), BinaryOp(left=Identifier('y'), op='+', right=Identifier('x'))]))

    def test_parse_simple_assignment(self) -> None:
        assert parse(tokenize('a = b')) == module(BinaryOp(left=Identifier('a'), op='=', right=Identifier('b')))

    def test_parse_simple_assignment_with_expression(self) -> None:
        assert parse(tokenize('a = b + c')) == module(BinaryOp(left=Identifier('a'), op='=', right=BinaryOp(left=Identifier('b'), op='+', right=Identifier('c'))))
    
    def test_parse_unary_op(self) -> None:
        assert parse(tokenize('-2')) == module(UnaryOp(right=Literal(2), op='-'))

    def test_parse_unary_op_not(self) -> None:
        assert parse(tokenize('not false')) == module(UnaryOp(right=Literal(False), op='not'))
    
    def test_parse_expression_with_unary_op(self) -> None:
        assert parse(tokenize('((-2)+3)')) == module(BinaryOp(
            left=UnaryOp(op='-', right=Literal(2)),
            op='+',
            right=Literal(3)
        ))

    def test_parse_expression_with_unary_op_and_binaries(self) -> None:
        assert parse(tokenize('((-2)+3)-6')) == module(BinaryOp(
            left=BinaryOp(
                left=UnaryOp(op='-', right=Literal(2)),
                op='+',
                right=Literal(3)
            ),
            op='-',
            right=Literal(6)
        ))

    def test_parse_expression_with_different_precedence(self) -> None:
        assert parse(tokenize('2-3+4*5')) == module(BinaryOp(
            left=BinaryOp(
                left=Literal(2),
                op='-',
                right=Literal(3)
            ),
            op='+',
            right=BinaryOp(
                left=Literal(4),
                op='*',
                right=Literal(5)
            )
        ))

    def test_parse_expression_with_unary_op_and_binaries_2(self) -> None:
        assert parse(tokenize('((-2)+3)-6*3')) == module(BinaryOp(
            left=BinaryOp(
                left=UnaryOp(op='-', right=Literal(2)),
                op='+',
                right=Literal(3)
            ),
            op='-',
            right=BinaryOp(
                left=Literal(6), 
                op='*', 
                right=Literal(3)
            )
        ))

    def test_parse_operators_in_correct_precedence(self) -> None:
        assert parse(tokenize('((-2)+3)-6*3%7/1<-5')) == module(BinaryOp(
            left=BinaryOp(
                left=BinaryOp(
                    left=UnaryOp(right=Literal(2), op='-'),
                    op='+',
                    right=Literal(3)
                ),
                op='-',
                right=BinaryOp(
                    left=BinaryOp(
                        left=BinaryOp(
                            left=Literal(6),
                            op='*',
                            right=Literal(3)
                        ),
                        op='%',
                        right=Literal(7)
                    ),
                    op='/',
                    right=Literal(1)
                )
            ),
            op='<',
            right=UnaryOp(op='-', right=Literal(5))
        ))

    def test_parse_top_level_vars(self) -> None:
        assert parse(tokenize('var a = 1;var b = 2; var c = 3; var d = 4')) == module([
            Var(name=Identifier('a'), initialization=Literal(1)),
            Var(name=Identifier('b'), initialization=Literal(2)),
            Var(name=Identifier('c'), initialization=Literal(3)),
            Var(name=Identifier('d'), initialization=Literal(4))
        ])

    def test_parse_single_var(self) -> None:
        assert parse(tokenize('var a = 1')) == module(Var(name=Identifier('a'), initialization=Literal(1)))

    def test_parse_single_var_with_semi_colon(self) -> None:
        assert parse(tokenize('var a = 1;')) == module([
            Var(name=Identifier('a'), initialization=Literal(1)), 
            Literal(None)
        ])

    def test_parse_doublw_vars(self) -> None:
        assert parse(tokenize('var a = 1;var b=2')) == module([Var(name=Identifier('a'), initialization=Literal(1)), Var(name=Identifier('b'), initialization=Literal(2))])

    def test_parse_double_vars_with_semi_colon(self) -> None:
        assert parse(tokenize('var a = 1;var b=2;')) == module([
            Var(name=Identifier('a'), initialization=Literal(1)), 
            Var(name=Identifier('b'), initialization=Literal(2)), 
            Literal(None)
        ])

    def test_parse_block_simple(self) -> None:
        assert parse(tokenize('x = {f(a);x = y;f(x);}')) == module(BinaryOp(
            left=Identifier('x'), 
            op='=', 
            right=Block(statements=[
                FuncCall(name=Identifier('f'), args=[Identifier('a')]),
                BinaryOp(left=Identifier('x'), op='=', right=Identifier('y')),
                FuncCall(name=Identifier('f'), args=[Identifier('x')]),
                Literal(value=None)
            ])))

    def test_parse_block_simple_2(self) -> None:
        assert parse(tokenize('x = {y;z}')) == module(BinaryOp(
            left=Identifier('x'), 
            op='=', 
            right=Block(statements=[
                Identifier('y'),
                Identifier('z'),
            ])))

    def test_parse_inner_blocks(self) -> None:
        assert parse(tokenize('{ { a } { b } }')) == module(Block(
            statements=[
                Block(statements=[Identifier('a')]), 
                Block(statements=[Identifier('b')])
            ]
        ))

    def test_parse_inner_blocks_with_semi_colons(self) -> None:
        assert parse(tokenize('{ { a }; { b } }')) == module(Block(
            statements=[
                Block(statements=[Identifier('a')]), 
                Block(statements=[Identifier('b')])
            ]
        ))

    def test_parse_blocks_with_ifs(self) -> None:
        assert parse(tokenize('{ if true then { a }; b }')) == module(Block(
            statements=[
                IfThenElse(
                    cond=Literal(True), 
                    then=Block(statements=[Identifier('a')])
                ),
                Identifier('b')
            ]
        ))

    def test_parse_blocks_with_ifs_without_semi_colon(self) -> None:
        assert parse(tokenize('{ if true then { a } b }')) == module(Block(
            statements=[
                IfThenElse(
                    cond=Literal(True), 
                    then=Block(statements=[Identifier('a')])
                ),
                Identifier('b')
            ]
        ))

    def test_parse_block_with_ifs_and_expressions(self) -> None:
        assert parse(tokenize('{ if true then { a } b; c }')) == module(Block(
            statements=[
                IfThenElse(cond=Literal(True), then=Block(statements=[Identifier('a')])),
                Identifier('b'),
                Identifier('c')
            ]
        ))

    def test_parse_block_with_ifs_else_and_expressions(self) -> None:
        assert parse(tokenize('{ if true then { a } else { b } c }')) == module(Block(
            statements=[
                IfThenElse(cond=Literal(True), then=Block(statements=[Identifier('a')]), otherwise=Block(statements=[Identifier('b')])),
                Identifier('c')
            ]
        ))
    
    def test_parse_block_assignment_with_inner_blocks(self) -> None:
        assert parse(tokenize('x = { { f(a) } { b } }')) == module(BinaryOp(
            left=Identifier('x'),
            op='=',
            right=Block(statements=[Block(statements=[FuncCall(args=[Identifier('a')], name=Identifier('f'))]), Block(statements=[Identifier('b')])])
        ))
    
    def test_parse_parens_with_block(self) -> None:
        assert parse(tokenize('({})')) == module(Block(statements=[Literal(None)]))
    
    def test_parse_blocks_with_while_blocks(self) -> None:
        assert parse(tokenize('{while false do {b;};}')) == module(Block(statements=[
            While(cond=Literal(False), body=Block(statements=[Identifier('b'), Literal(None)])),
            Literal(None)
        ]))
    
    def test_parse_blocks_with_parens_and_functions(self) -> None:
        assert parse(tokenize('{a = (1+2)/3; func(a,y)}')) == module(Block(statements=[
            BinaryOp(
                left=Identifier('a'), 
                op='=', 
                right=BinaryOp(
                    left=BinaryOp(
                        left=Literal(1), 
                        op='+', 
                        right=Literal(2)
                    ), 
                    op='/',
                    right=Literal(3)
                )
            ),
            FuncCall(name=Identifier('func'), args=[Identifier('a'), Identifier('y')])
        ]))
    
    def test_parse_if_then_else_with_blocks(self) -> None:
        assert parse(tokenize('if true then 1 else {a};')) == module([
            IfThenElse(cond=Literal(True), then=Literal(1), otherwise=Block(statements=[Identifier('a')])),
            Literal(None)
        ])

    def test_parse_while_with_blocks(self) -> None:
        assert parse(tokenize('while true do {a}')) == module(While(cond=Literal(True), body=Block(statements=[Identifier('a')])))
    
    def test_parse_while_with_blocks_and_semi_colon(self) -> None:
        assert parse(tokenize('while true do {a};')) == module([
            While(cond=Literal(True), body=Block(statements=[Identifier('a')])),
            Literal(None)
        ])
    
    def test_parse_while_with_blocks_and_semi_colons(self) -> None:
        assert parse(tokenize('while true do {a;};')) == module([While(cond=Literal(True), body=Block(statements=[Identifier('a'), Literal(None)])), Literal(None)])
    
    def test_parse_while_with_var_and_blocks_and_semi_colons(self) -> None:
        assert parse(tokenize('{var a = 1; while true do {a}}')) == module( Block(
            statements=[
                Var(name=Identifier('a'),initialization=Literal(1)),
                While(cond=Literal(True), body=Block(statements=[Identifier('a')]))
            ]
        ))

    def test_parse_while_with_var_and_blocks_and_semi_colons_and_reassigns(self) -> None:
        assert parse(tokenize('var x = 1; while x<3 do {x=x+1}')) == module([
            Var(name=Identifier('x'),initialization=Literal(1)),
            While(cond=BinaryOp(left=Identifier('x'), op='<', right=Literal(3)), 
                    body=Block(statements=[BinaryOp(left=Identifier('x'), op='=', right=BinaryOp(left=Identifier('x'), op='+', right=Literal(1)))]))
        ])

    def test_parse_var_with_block(self) -> None:
        assert parse(tokenize('var a = {1+1};')) == module([
            Var(name=Identifier('a'), initialization=Block(statements=[BinaryOp(left=Literal(1), op='+', right=Literal(1))])), 
            Literal(None)
        ])

    def test_parse_binary_op_with_block(self) -> None:
        assert parse(tokenize('a = {1+1};')) == module([BinaryOp(left=Identifier('a'), op='=', right=Block(statements=[BinaryOp(left=Literal(1), op='+', right=Literal(1))])), Literal(None)])

    def test_parse_top_level_with_block(self) -> None:
        assert parse(tokenize('{};')) == module([
            Block(statements=[Literal(None)]), 
            Literal(None)
        ])
    
    def test_parse_block_with_var(self) -> None:
        assert parse(tokenize('{var a = 1+1; 1+a}')) == module( Block(statements=[Var(name=Identifier('a'), initialization=BinaryOp(left=Literal(1), op='+', right=Literal(1))), BinaryOp(left=Literal(1), op='+', right=Identifier('a'))]))
    
    def test_parse_variable_with_type(self) -> None:
        assert parse(tokenize('var test: Int = true')) == module( Var(name=Identifier('test'), declared_type=Int, initialization=Literal(True)))

    def test_parse_variable_with_unknown_type(self) -> None:
        assert parse(tokenize('var test: int = true')) == module( Var(name=Identifier('test'), declared_type=Unknown, initialization=Literal(True)))

    def test_parse_basic_program(self) -> None:
        assert parse(tokenize('var x = if true then {var a = 2; a*5} else {-1}; x')) == module([
             Var(name=Identifier('x'), initialization=IfThenElse(cond=Literal(True), then=Block(statements=[
                Var(name=Identifier('a'), initialization=Literal(2)),
                BinaryOp(left=Identifier('a'), op='*', right=Literal(5))
            ]), otherwise=Block(statements=[UnaryOp(op='-', right=Literal(1))]))),
            Identifier('x')
        ])

    def test_parse_basic_program2(self) -> None:
        assert parse(tokenize('var y = 3; var t = true; var x = if t then {var a = 2; a*y} else {-1}; x')) == module([
            Var(name=Identifier('y'), initialization=Literal(3)),
            Var(name=Identifier('t'), initialization=Literal(True)),
            Var(name=Identifier('x'), initialization=IfThenElse(cond=Identifier('t'), then=Block(statements=[
                Var(name=Identifier('a'), initialization=Literal(2)),
                BinaryOp(left=Identifier('a'), op='*', right=Identifier('y'))
            ]), otherwise=Block(statements=[UnaryOp(op='-', right=Literal(1))]))),
            Identifier('x')
        ])

    def test_parse_many_vars(self) -> None:
        assert parse(tokenize('var a = {} var x = 1;')) == module([
            Var(name=Identifier('a'), initialization=Block(statements=[Literal(None)])),
            Var(name=Identifier('x'), initialization=Literal(1)),
            Literal(None)
        ])

    def test_parse_basic_program3(self) -> None:
        assert parse(tokenize('var max = -999; {while max < 0 do {max = max+1;}}; max')) == module([
            Var(name=Identifier('max'), initialization=UnaryOp(op='-', right=Literal(999))),
            Block(statements=[While(cond=BinaryOp(left=Identifier('max'), op='<', right=Literal(0)), body=Block(statements=[
                BinaryOp(left=Identifier('max'), op='=', right=BinaryOp(left=Identifier('max'), op='+', right=Literal(1))), 
                Literal(None)
            ]))]),
            Identifier('max')
        ])
    
    def test_parse_basic_program4(self) -> None:
        assert parse(tokenize('while true do {if 1 > 0 then { if 2 > 1 then 4 } else { if 5 < 6 then 7}}')) == module(While(
            cond=Literal(True),
            body=Block(statements=[
                IfThenElse(cond=BinaryOp(Literal(1), '>', Literal(0)),
                           then=Block(statements=[IfThenElse(cond=BinaryOp(Literal(2), '>', Literal(1)), then=Literal(4))]),
                           otherwise=Block(statements=[IfThenElse(cond=BinaryOp(Literal(5), '<', Literal(6)), then=Literal(7))]))
            ])
        ))

    def test_parse_basic_program5(self) -> None:
        assert parse(tokenize('while true do {if 1 > 0 then { while false do {} } else while false do {}}')) == module(While(
            cond=Literal(True),
            body=Block(statements=[
                IfThenElse(cond=BinaryOp(Literal(1), '>', Literal(0)),
                           then=Block(statements=[While(cond=Literal(False), body=Block(statements=[Literal(None)]))]),
                           otherwise=While(cond=Literal(False), body=Block(statements=[Literal(None)])))
            ])
        ))

    def test_parse_function_def(self) -> None:
        assert parse(tokenize('fun do() {}')) == module(FuncDef(Identifier('do'), [], Block([Literal(None)])))

    def test_parse_function_def_with_type(self) -> None:
        assert parse(tokenize('fun do(): Int {}')) == module(FuncDef(Identifier('do'), [], Block([Literal(None)]), Int))

    def test_parse_function_def_with_type_with_semi_colon(self) -> None:
        assert parse(tokenize('fun do(): Int {};')) == module([FuncDef(Identifier('do'), [], Block([Literal(None)]), Int), Literal(None)])

    def test_parse_function_def_with_types(self) -> None:
        assert parse(tokenize('fun do(x: Int, y: Bool) {}')) == module(FuncDef(Identifier('do'), [Argument(name='x', declared_type=Int), Argument(name='y', declared_type=Bool)], Block([Literal(None)])))

    def test_parse_function_def_with_type_with_return_type(self) -> None:
        assert parse(tokenize('fun do(x: Int, y: Bool): Int {}')) == module(FuncDef(Identifier('do'), [Argument(name='x', declared_type=Int), Argument(name='y', declared_type=Bool)], Block([Literal(None)]), Int))

    def test_parse_function_def_with_function_call(self) -> None:
        assert parse(tokenize('fun do(): Unit {1+1;};do()')) == module([FuncDef(Identifier('do'), [], Block([BinaryOp(Literal(1), '+', Literal(1)),Literal(None)]), Unit), FuncCall([], Identifier('do'))])

    def test_parse_function_call_inside_func_def(self) -> None:
        assert parse(tokenize('fun do(): Int {1+1};fun do2(): Int {do()}; do2()')) == module([
            FuncDef(Identifier('do'), [], Block([BinaryOp(Literal(1), '+', Literal(1))]), Int),
            FuncDef(Identifier('do2'), [], Block([FuncCall([], Identifier('do'))]), Int),
            FuncCall([], Identifier('do2')) 
        ])

    def test_parse_function_call_binary_op(self) -> None:
        assert parse(tokenize('fun square_and_add(x: Int, y: Int): Int {x*x+y}; square_and_add(8,6)')) == module([
            FuncDef(Identifier('square_and_add'), [Argument('x', Int), Argument('y', Int)], Block([BinaryOp(BinaryOp(Identifier('x'), '*', Identifier('x')), '+', Identifier('y'))]), Int),
            FuncCall([Literal(8), Literal(6)], Identifier('square_and_add'))
        ])

    def test_parse_function_call_with_binary_op(self) -> None:
        assert parse(tokenize('s(1,1) + f(3,3)')) == module(BinaryOp(
            FuncCall([Literal(1), Literal(1)], Identifier('s')),
            '+',
            FuncCall([Literal(3), Literal(3)], Identifier('f'))
        ))

    def test_parse_function_program(self) -> None:
        assert parse(tokenize('fun square(x: Int): Int { x * x } fun vec_len_squared(x: Int, y: Int): Int { square(x) + square(y) } fun print_int_twice(x: Int) { print_int(x); print_int(x); } print_int_twice(vec_len_squared(3, 4))')) == module([
            FuncDef(Identifier('square'), [Argument('x', Int)], Block([BinaryOp(Identifier('x'), '*', Identifier('x'))]), Int),
            FuncDef(Identifier('vec_len_squared'), [Argument('x', Int), Argument('y', Int)], Block([BinaryOp(FuncCall([Identifier('x')], Identifier('square')), '+', FuncCall([Identifier('y')], Identifier('square')))]), Int),
            FuncDef(Identifier('print_int_twice'), [Argument('x', Int)], Block([FuncCall([Identifier('x')], Identifier('print_int')), FuncCall([Identifier('x')], Identifier('print_int')), Literal(None)]), None),
            FuncCall([FuncCall([Literal(3), Literal(4)], Identifier('vec_len_squared'))], Identifier('print_int_twice'))
        ])

    def test_parse_unary_operator(self) -> None:
        assert parse(tokenize('-p * -p')) == module(
            BinaryOp(UnaryOp('-', Identifier('p')), '*', UnaryOp('-', Identifier('p')))
        )

    def test_parse_deference_operator(self) -> None:
        assert parse(tokenize('*p * *p')) == module(
            BinaryOp(UnaryOp('*', Identifier('p')), '*', UnaryOp('*', Identifier('p')))
        )

    def test_parse_deference_and_unary_minus_operator(self) -> None:
        assert parse(tokenize('var p = *p * -p')) == module(
            Var(Identifier('p'), BinaryOp(UnaryOp('*', Identifier('p')), '*', UnaryOp('-', Identifier('p'))))
        )

    def test_parse_unary_with_block(self) -> None:
        assert parse(tokenize('-{1+1}')) == module(
            UnaryOp('-', Block([BinaryOp(Literal(1), '+', Literal(1))]))
        )

    def test_parse_int_pointer(self) -> None:
        pointer = Pointer()
        pointer.value = Int
        assert parse(tokenize('var x: Int* = &y')) == module(
            Var(Identifier('x'), UnaryOp('&', Identifier('y')), pointer)
        )

    def test_parse_int_pointer_to_pointers(self) -> None:
        pointer = Pointer()
        pointer.value = Pointer()
        pointer.value.value = Pointer()
        pointer.value.value.value = Int
        assert parse(tokenize('var x: Int*** = &y')) == module(
            Var(Identifier('x'), UnaryOp('&', Identifier('y')), pointer)
        )

    def test_parse_pointers_with_pointers_to_pointers(self) -> None:
        pointer_x = Pointer()
        pointer_x.value = Int

        pointer_y = Pointer()
        pointer_y.value = pointer_x
        assert parse(tokenize('var x: Int = 1; var y: Int* = &x; var z: Int** = &y;')) == module([
            Var(Identifier('x'), Literal(1), Int),
            Var(Identifier('y'), UnaryOp('&', Identifier('x')), pointer_x),
            Var(Identifier('z'), UnaryOp('&', Identifier('y')), pointer_y),
            Literal(None)
        ])

    def test_parse_multi_unary_operators(self) -> None:
        assert parse(tokenize('var x: Int = --2; x')) == module([
            Var(Identifier('x'), UnaryOp('-', UnaryOp('-', Literal(2))), Int),
            Identifier('x')
        ])

    def test_parse_multi_unary_dereference_op(self) -> None:
        pointer = Pointer()
        pointer.value = Int

        pointer2 = Pointer()
        pointer2.value = Pointer()
        pointer2.value.value = Int
        assert parse(tokenize('var x: Int = 1; var y: Int* = &x; var z: Int** = &y; var n: Int = **z')) == module([
            Var(Identifier('x'), Literal(1), Int),
            Var(Identifier('y'), UnaryOp('&', Identifier('x')), pointer),
            Var(Identifier('z'), UnaryOp('&', Identifier('y')), pointer2),
            Var(Identifier('n'), UnaryOp('*', UnaryOp('*', Identifier('z'))), Int)
        ])


    def test_parse_break_and_continue(self) -> None:
        assert parse(tokenize('while true do { if true then break else continue }')) == module(
            While(Literal(True), Block([
                IfThenElse(Literal(True), BreakContinue('break'), BreakContinue('continue'))
            ]))
        )

    def test_parse_erroneous_block(self) -> None:
        self.assertRaises(Exception, parse, tokenize('{ a b }'))

    def test_parse_erroneous_if_within_block(self) -> None:
        self.assertRaises(Exception, parse, tokenize('{ if true then { a } b c }'))

    def test_parse_erroneous_double_semi_colon(self) -> None:
        self.assertRaises(Exception, parse, tokenize('while { a } do { b };;'))

    def test_parse_erroneous_input(self) -> None:
        self.assertRaises(Exception, parse, tokenize('a + b c'))

    def test_parse_erroneous_input_2(self) -> None:
        self.assertRaises(Exception, parse, tokenize('_a + b) * 2'))

    def test_parse_erroneous_input_3(self) -> None:
        self.assertRaises(Exception, parse, tokenize('(12 + b) * 2 / (2 + 2) */ 2'))

    def test_parse_erroneous_var(self) -> None:
        self.assertRaises(Exception, parse, tokenize('var 1 = 2'))

    def test_parse_erroneous_vars(self) -> None:
        self.assertRaises(Exception, parse, tokenize('var a = b var g = 1'))

    def test_parse_erroneous_func_call(self) -> None:
        self.assertRaises(Exception, parse, tokenize('f(x'))

    def test_parse_erroneous_func_call_2(self) -> None:
        self.assertRaises(Exception, parse, tokenize('f(x,y'))

    def test_parse_erroneous_func_call_3(self) -> None:
        self.assertRaises(Exception, parse, tokenize('f(x, var y: Int = 2;)'))

    def test_parse_erroneous_unary_op(self) -> None:
        self.assertRaises(Exception, parse, tokenize('&2'))

    def test_parse_erroneuos_func_def(self) -> None:
        self.assertRaises(Exception, parse, tokenize('fun 1(x: Int, y: Int): Unit {}'))

    def test_parse_erroneuos_func_def2(self) -> None:
        self.assertRaises(Exception, parse, tokenize('fun f(1: Int, y: Int): Unit {}'))

    def test_parse_erroneuos_var_type_declaration(self) -> None:
        self.assertRaises(Exception, parse, tokenize('var x: 1 = 23'))