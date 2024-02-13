from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.interpreter import interpret, SymbolTable
from compiler.ast import Expression

import unittest

def p(input: str) -> Expression:
    return parse(tokenize(input))

class InterpreterTest(unittest.TestCase):
    def test_interpret_simple(self):
        assert interpret(p('1 + 2'), SymbolTable({}, None)) == 3

    def test_interpret_simple_if(self):
        assert interpret(p('if 5 < 10 then 2*5'), SymbolTable({}, None)) == 10

    def test_interpret_simple_if_else(self):
        assert interpret(p('if 5 < 2 then 2*5 else 6/2'), SymbolTable({}, None)) == 3
  
    def test_interpret_simple_var(self):
        sym = SymbolTable({}, None)
        interpret(p('var a = 1'), sym)
        assert sym.bindings['a'] == 1