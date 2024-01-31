from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.ast import Expression, BinaryOp, Literal, Identifier, IfThenElse

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
    
    def test_parse_erroneous_input(self):
        self.assertRaises(Exception, parse, tokenize('a + b c'))
    
    def test_parse_erroneous_input_2(self):
        self.assertRaises(Exception, parse, tokenize('_a + b) * 2'))

    def test_parse_erroneous_input_3(self):
        self.assertRaises(Exception, parse, tokenize('(12 + b) * 2 / (2 + 2) ** 2'))