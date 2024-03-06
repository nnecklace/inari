from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.ast import Expression, BinaryOp, Literal, Identifier, IfThenElse, FuncCall, UnaryOp, Block, Var, While, Module
from compiler.types import Int, Unit, Unknown

import unittest

def module(expressions: list[Expression] | Expression) -> Module:
    if isinstance(expressions, Expression):
       return Module('main', [expressions])
    
    return Module('main', expressions)

class ParserTest(unittest.TestCase):
    def test_basic_parser(self):
        assert parse(tokenize('1+2')) == module(BinaryOp(left=Literal(1), op='+', right=Literal(2)))

    def test_parser_with_complicated_expression(self):
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

    def test_parse_from_high_to_low_precedence(self):
        assert parse(tokenize('b*b+2')) == module(BinaryOp(
            left=BinaryOp(
                left=Identifier('b'),
                op='*',
                right=Identifier('b')
            ),
            op='+',
            right=Literal(2)
        ))

    def test_parse_simple_if(self):
        assert parse(tokenize('if a then b')) == module(IfThenElse(cond=Identifier(name='a'), then=Identifier(name='b')))

    def test_parse_simple_if_else(self):
        assert parse(tokenize('if a then b else c')) == module(IfThenElse(cond=Identifier(name='a'), then=Identifier(name='b'), otherwise=Identifier('c')))

    def test_parse_simple_if_arithmetic(self):
        assert parse(tokenize('if a + 4 then b*b+2 else c-4')) == module(IfThenElse(
            cond=BinaryOp(left=Identifier(name='a'), op='+', right=Literal(4)),
            then=BinaryOp(left=BinaryOp(left=Identifier('b'), op='*', right=Identifier('b')), op='+', right=Literal(2)),
            otherwise=BinaryOp(left=Identifier('c'), op='-', right=Literal(4))
        ))

    def test_parse_if_as_part_of_expression(self):
        assert parse(tokenize('1 + if true then 2 else 3')) == module(BinaryOp(
            left=Literal(1),
            op='+',
            right=IfThenElse(
                cond=Literal(True),
                then=Literal(2),
                otherwise=Literal(3)
            )
        ))
    
    def test_parse_function_calls_simple(self):
        assert parse(tokenize('f(x)')) == module(FuncCall(name='f', args=[Identifier('x')]))

    def test_parse_function_calls_multi_args(self):
        assert parse(tokenize('f(x,y,z)')) == module(FuncCall(name='f', args=[Identifier('x'), Identifier('y'), Identifier('z')]))
    
    def test_parse_function_calls_with_expression(self):
        assert parse(tokenize('f(x+y)')) == module(FuncCall(name='f', args=[BinaryOp(left=Identifier('x'), op='+', right=Identifier('y'))]))

    def test_parse_function_calls_with_expression_with_parens(self):
        assert parse(tokenize('f((x+y)+z)')) == module(FuncCall(name='f', args=[BinaryOp(left=BinaryOp(left=Identifier('x'), op='+', right=Identifier('y')), op='+', right=Identifier('z'))]))

    def test_parse_function_calls_with_expression_with_parens2(self):
        assert parse(tokenize('f((x+y)+z+(y+8))')) == module(FuncCall(name='f', args=[
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
    
    def test_parse_function_calls_with_many_parens(self):
        assert parse(tokenize('f((((((((((((((1+1))))))))))))))')) == module(FuncCall(name='f', args=[BinaryOp(left=Literal(1),op='+',right=Literal(1))]))
    
    def test_parse_function_calls_with_nested_function_calls(self):
        assert parse(tokenize('f(g(x), h(m(n(y))))')) == module(FuncCall(name='f', args=[FuncCall(name='g', args=[Identifier('x')]), FuncCall(name='h',args=[FuncCall(name='m', args=[FuncCall(name='n',args=[Identifier('y')])])])]))

    def test_parse_function_calls_with_nested_function_call_and_expression(self):
        assert parse(tokenize('f(x, g(x), y+x)')) == module(FuncCall(name='f', args=[Identifier('x'), FuncCall(name='g', args=[Identifier('x')]), BinaryOp(left=Identifier('y'), op='+', right=Identifier('x'))]))

    def test_parse_simple_assignment(self):
        assert parse(tokenize('a = b')) == module(BinaryOp(left=Identifier('a'), op='=', right=Identifier('b')))

    def test_parse_simple_assignment_with_expression(self):
        assert parse(tokenize('a = b + c')) == module(BinaryOp(left=Identifier('a'), op='=', right=BinaryOp(left=Identifier('b'), op='+', right=Identifier('c'))))
    
    def test_parse_unary_op(self):
        assert parse(tokenize('-2')) == module(UnaryOp(right=Literal(2), op='-'))

    def test_parse_unary_op_not(self):
        assert parse(tokenize('not false')) == module(UnaryOp(right=Literal(False), op='not'))
    
    def test_parse_expression_with_unary_op(self):
        assert parse(tokenize('((-2)+3)')) == module(BinaryOp(
            left=UnaryOp(op='-', right=Literal(2)),
            op='+',
            right=Literal(3)
        ))

    def test_parse_expression_with_unary_op_and_binaries(self):
        assert parse(tokenize('((-2)+3)-6')) == module(BinaryOp(
            left=BinaryOp(
                left=UnaryOp(op='-', right=Literal(2)),
                op='+',
                right=Literal(3)
            ),
            op='-',
            right=Literal(6)
        ))

    def test_parse_expression_with_different_precedence(self):
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

    def test_parse_expression_with_unary_op_and_binaries_2(self):
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

    def test_parse_operators_in_correct_precedence(self):
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

    def test_parse_top_level_vars(self):
        assert parse(tokenize('var a = 1;var b = 2; var c = 3; var d = 4')) == module([
            Var(name=Identifier('a'), initialization=Literal(1)),
            Var(name=Identifier('b'), initialization=Literal(2)),
            Var(name=Identifier('c'), initialization=Literal(3)),
            Var(name=Identifier('d'), initialization=Literal(4))
        ])

    def test_parse_single_var(self):
        assert parse(tokenize('var a = 1')) == module(Var(name=Identifier('a'), initialization=Literal(1)))

    def test_parse_single_var_with_semi_colon(self):
        assert parse(tokenize('var a = 1;')) == module([
            Var(name=Identifier('a'), initialization=Literal(1)), 
            Literal(None)
        ])

    def test_parse_doublw_vars(self):
        assert parse(tokenize('var a = 1;var b=2')) == module([Var(name=Identifier('a'), initialization=Literal(1)), Var(name=Identifier('b'), initialization=Literal(2))])

    def test_parse_double_vars_with_semi_colon(self):
        assert parse(tokenize('var a = 1;var b=2;')) == module([
            Var(name=Identifier('a'), initialization=Literal(1)), 
            Var(name=Identifier('b'), initialization=Literal(2)), 
            Literal(None)
        ])

    def test_parse_block_simple(self):
        assert parse(tokenize('x = {f(a);x = y;f(x);}')) == module(BinaryOp(
            left=Identifier('x'), 
            op='=', 
            right=Block(statements=[
                FuncCall(name='f', args=[Identifier('a')]),
                BinaryOp(left=Identifier('x'), op='=', right=Identifier('y')),
                FuncCall(name='f', args=[Identifier('x')]),
                Literal(value=None)
            ])))

    def test_parse_block_simple_2(self):
        assert parse(tokenize('x = {y;z}')) == module(BinaryOp(
            left=Identifier('x'), 
            op='=', 
            right=Block(statements=[
                Identifier('y'),
                Identifier('z'),
            ])))

    def test_parse_inner_blocks(self):
        assert parse(tokenize('{ { a } { b } }')) == module(Block(
            statements=[
                Block(statements=[Identifier('a')]), 
                Block(statements=[Identifier('b')])
            ]
        ))

    def test_parse_inner_blocks_with_semi_colons(self):
        assert parse(tokenize('{ { a }; { b } }')) == module(Block(
            statements=[
                Block(statements=[Identifier('a')]), 
                Block(statements=[Identifier('b')])
            ]
        ))

    def test_parse_blocks_with_ifs(self):
        assert parse(tokenize('{ if true then { a }; b }')) == module(Block(
            statements=[
                IfThenElse(
                    cond=Literal(True), 
                    then=Block(statements=[Identifier('a')])
                ),
                Identifier('b')
            ]
        ))

    def test_parse_blocks_with_ifs_without_semi_colon(self):
        assert parse(tokenize('{ if true then { a } b }')) == module(Block(
            statements=[
                IfThenElse(
                    cond=Literal(True), 
                    then=Block(statements=[Identifier('a')])
                ),
                Identifier('b')
            ]
        ))

    def test_parse_block_with_ifs_and_expressions(self):
        assert parse(tokenize('{ if true then { a } b; c }')) == module(Block(
            statements=[
                IfThenElse(cond=Literal(True), then=Block(statements=[Identifier('a')])),
                Identifier('b'),
                Identifier('c')
            ]
        ))

    def test_parse_block_with_ifs_else_and_expressions(self):
        assert parse(tokenize('{ if true then { a } else { b } c }')) == module(Block(
            statements=[
                IfThenElse(cond=Literal(True), then=Block(statements=[Identifier('a')]), otherwise=Block(statements=[Identifier('b')])),
                Identifier('c')
            ]
        ))
    
    def test_parse_block_assignment_with_inner_blocks(self):
        assert parse(tokenize('x = { { f(a) } { b } }')) == module(BinaryOp(
            left=Identifier('x'),
            op='=',
            right=Block(statements=[Block(statements=[FuncCall(args=[Identifier('a')], name='f')]), Block(statements=[Identifier('b')])])
        ))
    
    def test_parse_parens_with_block(self):
        assert parse(tokenize('({})')) == module(Block(statements=[Literal(type=Unit, location=None, value=None)]))
    
    def test_parse_blocks_with_while_blocks(self):
        assert parse(tokenize('{while false do {b;};}')) == module(Block(statements=[
            While(cond=Literal(False), body=Block(statements=[Identifier('b'), Literal(None)])),
            Literal(None)
        ]))
    
    def test_parse_blocks_with_parens_and_functions(self):
        assert parse(tokenize('{a = (1+2)/3; fun(a,y)}')) == module(Block(statements=[
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
            FuncCall(name='fun', args=[Identifier('a'), Identifier('y')])
        ]))
    
    def test_parse_if_then_else_with_blocks(self):
        assert parse(tokenize('if true then 1 else {a};')) == module([
            IfThenElse(cond=Literal(True), then=Literal(1), otherwise=Block(statements=[Identifier('a')])),
            Literal(None)
        ])

    def test_parse_while_with_blocks(self):
        assert parse(tokenize('while true do {a}')) == module(While(cond=Literal(True), body=Block(statements=[Identifier('a')])))
    
    def test_parse_while_with_blocks_and_semi_colon(self):
        assert parse(tokenize('while true do {a};')) == module([
            While(cond=Literal(True), body=Block(statements=[Identifier('a')])),
            Literal(None)
        ])
    
    def test_parse_while_with_blocks_and_semi_colons(self):
        assert parse(tokenize('while true do {a;};')) == module([While(cond=Literal(True), body=Block(statements=[Identifier('a'), Literal(None)])), Literal(None)])
    
    def test_parse_while_with_var_and_blocks_and_semi_colons(self):
        assert parse(tokenize('{var a = 1; while true do {a}}')) == module( Block(
            statements=[
                Var(name=Identifier('a'),initialization=Literal(1)),
                While(cond=Literal(True), body=Block(statements=[Identifier('a')]))
            ]
        ))

    def test_parse_while_with_var_and_blocks_and_semi_colons_and_reassigns(self):
        assert parse(tokenize('var x = 1; while x<3 do {x=x+1}')) == module([
            Var(name=Identifier('x'),initialization=Literal(1)),
            While(cond=BinaryOp(left=Identifier('x'), op='<', right=Literal(3)), 
                    body=Block(statements=[BinaryOp(left=Identifier('x'), op='=', right=BinaryOp(left=Identifier('x'), op='+', right=Literal(1)))]))
        ])

    def test_parse_var_with_block(self):
        assert parse(tokenize('var a = {1+1};')) == module([
            Var(name=Identifier('a'), initialization=Block(statements=[BinaryOp(left=Literal(1), op='+', right=Literal(1))])), 
            Literal(None)
        ])

    def test_parse_binary_op_with_block(self):
        assert parse(tokenize('a = {1+1};')) == module([BinaryOp(left=Identifier('a'), op='=', right=Block(statements=[BinaryOp(left=Literal(1), op='+', right=Literal(1))])), Literal(None)])

    def test_parse_top_level_with_block(self):
        assert parse(tokenize('{};')) == module([
            Block(statements=[Literal(None)]), 
            Literal(None)
        ])
    
    def test_parse_block_with_var(self):
        assert parse(tokenize('{var a = 1+1; 1+a}')) == module( Block(statements=[Var(name=Identifier('a'), initialization=BinaryOp(left=Literal(1), op='+', right=Literal(1))), BinaryOp(left=Literal(1), op='+', right=Identifier('a'))]))
    
    def test_parse_variable_with_type(self):
        assert parse(tokenize('var test: Int = true')) == module( Var(name=Identifier('test'), declared_type=Int, initialization=Literal(True)))

    def test_parse_variable_with_unknown_type(self):
        assert parse(tokenize('var test: int = true')) == module( Var(name=Identifier('test'), declared_type=Unknown, initialization=Literal(True)))

    def test_parse_basic_program(self):
        assert parse(tokenize('var x = if true then {var a = 2; a*5} else {-1}; x')) == module([
             Var(name=Identifier('x'), initialization=IfThenElse(cond=Literal(True), then=Block(statements=[
                Var(name=Identifier('a'), initialization=Literal(2)),
                BinaryOp(left=Identifier('a'), op='*', right=Literal(5))
            ]), otherwise=Block(statements=[UnaryOp(op='-', right=Literal(1))]))),
            Identifier('x')
        ])

    def test_parse_basic_program2(self):
        assert parse(tokenize('var y = 3; var t = true; var x = if t then {var a = 2; a*y} else {-1}; x')) == module([
            Var(name=Identifier('y'), initialization=Literal(3)),
            Var(name=Identifier('t'), initialization=Literal(True)),
            Var(name=Identifier('x'), initialization=IfThenElse(cond=Identifier('t'), then=Block(statements=[
                Var(name=Identifier('a'), initialization=Literal(2)),
                BinaryOp(left=Identifier('a'), op='*', right=Identifier('y'))
            ]), otherwise=Block(statements=[UnaryOp(op='-', right=Literal(1))]))),
            Identifier('x')
        ])

    def test_parse_many_vars(self):
        assert parse(tokenize('var a = {} var x = 1;')) == module([
            Var(name=Identifier('a'), initialization=Block(statements=[Literal(None)])),
            Var(name=Identifier('x'), initialization=Literal(1)),
            Literal(None)
        ])

    def test_parse_basic_program3(self):
        assert parse(tokenize('var max = -999; {while max < 0 do {max = max+1;}}; max')) == module([
            Var(name=Identifier('max'), initialization=UnaryOp(op='-', right=Literal(999))),
            Block(statements=[While(cond=BinaryOp(left=Identifier('max'), op='<', right=Literal(0)), body=Block(statements=[
                BinaryOp(left=Identifier('max'), op='=', right=BinaryOp(left=Identifier('max'), op='+', right=Literal(1))), 
                Literal(None)
            ]))]),
            Identifier('max')
        ])
    
    def test_parse_basic_program4(self):
        assert parse(tokenize('while true do {if 1 > 0 then { if 2 > 1 then 4 } else { if 5 < 6 then 7}}')) == module(While(
            cond=Literal(True),
            body=Block(statements=[
                IfThenElse(cond=BinaryOp(Literal(1), '>', Literal(0)),
                           then=Block(statements=[IfThenElse(cond=BinaryOp(Literal(2), '>', Literal(1)), then=Literal(4))]),
                           otherwise=Block(statements=[IfThenElse(cond=BinaryOp(Literal(5), '<', Literal(6)), then=Literal(7))]))
            ])
        ))

    def test_parse_basic_program4(self):
        assert parse(tokenize('while true do {if 1 > 0 then { while false do {} } else while false do {}}')) == module(While(
            cond=Literal(True),
            body=Block(statements=[
                IfThenElse(cond=BinaryOp(Literal(1), '>', Literal(0)),
                           then=Block(statements=[While(cond=Literal(False), body=Block(statements=[Literal(None)]))]),
                           otherwise=While(cond=Literal(False), body=Block(statements=[Literal(None)])))
            ])
        ))

    def test_parse_erroneous_block(self):
        self.assertRaises(Exception, parse, tokenize('{ a b }'))

    def test_parse_erroneous_if_within_block(self):
        self.assertRaises(Exception, parse, tokenize('{ if true then { a } b c }'))

    def test_parse_erroneous_double_semi_colon(self):
        self.assertRaises(Exception, parse, tokenize('while { a } do { b };;'))

    def test_parse_erroneous_input(self):
        self.assertRaises(Exception, parse, tokenize('a + b c'))

    def test_parse_erroneous_input_2(self):
        self.assertRaises(Exception, parse, tokenize('_a + b) * 2'))

    def test_parse_erroneous_input_3(self):
        self.assertRaises(Exception, parse, tokenize('(12 + b) * 2 / (2 + 2) ** 2'))

    def test_parse_erroneous_var(self):
        self.assertRaises(Exception, parse, tokenize('var 1 = 2'))

    def test_parse_erroneous_vars(self):
        self.assertRaises(Exception, parse, tokenize('var a = b var g = 1'))

    def test_parse_erroneous_func_call(self):
        self.assertRaises(Exception, parse, tokenize('f(x'))

    def test_parse_erroneous_func_call_2(self):
        self.assertRaises(Exception, parse, tokenize('f(x,y'))