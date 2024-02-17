from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.interpreter import interpret, top_level_symbol_table
from compiler.ast import Expression

import unittest

def p(input: str) -> Expression:
    return parse(tokenize(input))

def sym_table():
    return top_level_symbol_table

class InterpreterTest(unittest.TestCase):
    def test_interpret_simple(self):
        assert interpret(p('1 + 2'), sym_table()) == 3

    def test_interpret_simple_if(self):
        assert interpret(p('if 5 < 10 then 2*5'), sym_table()) == 10

    def test_interpret_simple_if_else(self):
        assert interpret(p('if 5 < 2 then 2*5 else 6/2'), sym_table()) == 3
  
    def test_interpret_simple_var(self):
        sym = sym_table()
        interpret(p('var a = 1'), sym)
        assert sym.bindings['a'] == 1

    def test_interpret_simple_block(self):
        assert interpret(p('{1+1}'), sym_table()) == 2
    
    def test_interpret_simple_block_2(self):
        assert interpret(p('{var a = 1+1; 1+a}'), sym_table()) == 3
    
    def test_interpret_simple_unary(self):
        assert interpret(p('-2'), sym_table()) == -2
    
    def test_interpret_simple_unary_not(self):
        assert interpret(p('not true'), sym_table()) == False

    def test_interpret_simple_reassignment(self):
        assert interpret(p('var x = 1;x+1'), sym_table()) == 2

    def test_interpret_simple_reassignment_with_block(self):
        assert interpret(p('var x = 1;{x=x+1}'), sym_table()) == 2
    
    def test_interpret_simple_while(self):
        assert interpret(p('var x = 1; while x<3 do {x=x+1}'), sym_table()) == 3
    
    def test_interpret_simple_and(self):
        assert interpret(p('var some = false;var some_else = true;some and {some_else = false;true};some_else'), sym_table()) == True

    def test_interpret_simple_or(self):
        assert interpret(p('var some = false;true or {some = true;true};some'), sym_table()) == False