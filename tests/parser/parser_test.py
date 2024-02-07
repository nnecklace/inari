from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.ast import Expression, BinaryOp, Literal, Identifier, IfThenElse, FuncCall, UnaryOp, Block, Var

import unittest

class ParserTest(unittest.TestCase):
    def test_basic_parser(self):
        assert parse(tokenize('1+2')) == BinaryOp(left=Literal(1), op='+', right=Literal(2))

    def test_parser_with_complicated_expression(self):
        assert parse(tokenize('(12 + b) * 2 / (2 + 2) * 2')) == BinaryOp(
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
        )
    
    def test_parse_from_high_to_low_precedence(self):
        assert parse(tokenize('b*b+2')) == BinaryOp(
            left=BinaryOp(
                left=Identifier('b'),
                op='*',
                right=Identifier('b')
            ),
            op='+',
            right=Literal(2)
        )
    
    def test_parse_simple_if(self):
        assert parse(tokenize('if a then b')) == IfThenElse(cond=Identifier(name='a'), then=Identifier(name='b'))

    def test_parse_simple_if_else(self):
        assert parse(tokenize('if a then b else c')) == IfThenElse(cond=Identifier(name='a'), then=Identifier(name='b'), otherwise=Identifier('c'))

    def test_parse_simple_if_arithmetic(self):
        assert parse(tokenize('if a + 4 then b*b+2 else c-4')) == IfThenElse(
            cond=BinaryOp(left=Identifier(name='a'), op='+', right=Literal(4)),
            then=BinaryOp(left=BinaryOp(left=Identifier('b'), op='*', right=Identifier('b')), op='+', right=Literal(2)),
            otherwise=BinaryOp(left=Identifier('c'), op='-', right=Literal(4))
        )

    def test_parse_if_as_part_of_expression(self):
        assert parse(tokenize('1 + if true then 2 else 3')) == BinaryOp(
            left=Literal(1),
            op='+',
            right=IfThenElse(
                cond=Identifier('true'),
                then=Literal(2),
                otherwise=Literal(3)
            )
        )
    
    def test_parse_function_calls_simple(self):
        assert parse(tokenize('f(x)')) == FuncCall(name='f', args=[Identifier('x')])

    def test_parse_function_calls_multi_args(self):
        assert parse(tokenize('f(x,y,z)')) == FuncCall(name='f', args=[Identifier('x'), Identifier('y'), Identifier('z')])
    
    def test_parse_function_calls_with_expression(self):
        assert parse(tokenize('f(x+y)')) == FuncCall(name='f', args=[BinaryOp(left=Identifier('x'), op='+', right=Identifier('y'))])

    def test_parse_function_calls_with_expression_with_parens(self):
        assert parse(tokenize('f((x+y)+z)')) == FuncCall(name='f', args=[BinaryOp(left=BinaryOp(left=Identifier('x'), op='+', right=Identifier('y')), op='+', right=Identifier('z'))])

    def test_parse_function_calls_with_expression_with_parens2(self):
        assert parse(tokenize('f((x+y)+z+(y+8))')) == FuncCall(name='f', args=[
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
            )
    
    def test_parse_function_calls_with_many_parens(self):
        assert parse(tokenize('f((((((((((((((1+1))))))))))))))')) == FuncCall(name='f', args=[BinaryOp(left=Literal(1),op='+',right=Literal(1))])
    
    def test_parse_function_calls_with_nested_function_calls(self):
        assert parse(tokenize('f(g(x), h(m(n(y))))')) == FuncCall(name='f', args=[FuncCall(name='g', args=[Identifier('x')]), FuncCall(name='h',args=[FuncCall(name='m', args=[FuncCall(name='n',args=[Identifier('y')])])])])

    def test_parse_function_calls_with_nested_function_call_and_expression(self):
        assert parse(tokenize('f(x, g(x), y+x)')) == FuncCall(name='f', args=[Identifier('x'), FuncCall(name='g', args=[Identifier('x')]), BinaryOp(left=Identifier('y'), op='+', right=Identifier('x'))])

    def test_parse_simple_assignment(self):
        assert parse(tokenize('a = b')) == BinaryOp(left=Identifier('a'), op='=', right=Identifier('b'))

    def test_parse_simple_assignment_with_expression(self):
        assert parse(tokenize('a = b + c')) == BinaryOp(left=Identifier('a'), op='=', right=BinaryOp(left=Identifier('b'), op='+', right=Identifier('c')))
    
    def test_parse_unary_op(self):
        assert parse(tokenize('-2')) == UnaryOp(right=Literal(2), op='-')
    
    def test_parse_expression_with_unary_op(self):
        assert parse(tokenize('((-2)+3)')) == BinaryOp(
            left=UnaryOp(op='-', right=Literal(2)),
            op='+',
            right=Literal(3)
        )

    # ((-2)+3)-6*3
    def test_parse_expression_with_unary_op_and_binaries(self):
        assert parse(tokenize('((-2)+3)-6')) == BinaryOp(
            left=BinaryOp(
                left=UnaryOp(op='-', right=Literal(2)),
                op='+',
                right=Literal(3)
            ),
            op='-',
            right=Literal(6)
        )

    def test_parse_expression_with_different_precedence(self):
        assert parse(tokenize('2-3+4*5')) == BinaryOp(
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
        )

    def test_parse_expression_with_unary_op_and_binaries_2(self):
        assert parse(tokenize('((-2)+3)-6*3')) == BinaryOp(
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
        )

    def test_parse_operators_in_correct_precedence(self):
        assert parse(tokenize('((-2)+3)-6*3%7/1<-5')) == BinaryOp(
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
        )

    def test_parse_top_level_vars(self):
        assert parse(tokenize('var a = 1;var b = 2; var c = 3; var d = 4')) == Block(
            statements=[
                Var(name=Identifier('a'), initialization=Literal(1)),
                Var(name=Identifier('b'), initialization=Literal(2)),
                Var(name=Identifier('c'), initialization=Literal(3)),
                Var(name=Identifier('d'), initialization=Literal(4))
            ]
        )

    def test_parse_block_simple(self):
        assert parse(tokenize('x = {f(a);x = y;f(x);}')) == BinaryOp(
            left=Identifier('x'), 
            op='=', 
            right=Block(statements=[
                FuncCall(name='f', args=[Identifier('a')]),
                BinaryOp(left=Identifier('x'), op='=', right=Identifier('y')),
                FuncCall(name='f', args=[Identifier('x')]),
                Literal(value=None)
            ]))

    def test_parse_erroneous_input(self):
        self.assertRaises(Exception, parse, tokenize('a + b c'))

    def test_parse_erroneous_input_2(self):
        self.assertRaises(Exception, parse, tokenize('_a + b) * 2'))

    def test_parse_erroneous_input_3(self):
        self.assertRaises(Exception, parse, tokenize('(12 + b) * 2 / (2 + 2) ** 2'))