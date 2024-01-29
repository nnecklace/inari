from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.ast import Expression, BinaryOp, Literal

import unittest

class ParserTest(unittest.TestCase):
    def test_basic_parser(self):
        print(parse(tokenize('1+2')))
        assert parse(tokenize('1+2')) == BinaryOp(left=Literal(1), op='+', right=Literal(2))