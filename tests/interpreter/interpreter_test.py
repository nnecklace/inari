from symtable import SymbolTable
from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.interpreter import interpret_module
from compiler.types import Value, get_global_symbol_table
from compiler.ast import Module

import unittest

def p(input: str) -> Module:
    return parse(tokenize(input))

class InterpreterTest(unittest.TestCase):
    def test_interpret_simple(self) -> None:
        assert interpret_module(p('1 + 2'), get_global_symbol_table()) == 3

    def test_interpret_simple_if(self) -> None:
        assert interpret_module(p('if 5 < 10 then 2*5'), get_global_symbol_table()) == 10

    def test_interpret_simple_if_else(self) -> None:
        assert interpret_module(p('if 5 < 2 then 2*5 else 6/2'), get_global_symbol_table()) == 3
  
    def test_interpret_simple_var(self) -> None:
        sym = get_global_symbol_table()
        interpret_module(p('var a = 1'), sym)
        assert sym.require('a') == 1

    def test_interpret_simple_block(self) -> None:
        assert interpret_module(p('{1+1}'), get_global_symbol_table()) == 2
    
    def test_interpret_simple_block_2(self) -> None:
        assert interpret_module(p('{var a = 1+1; 1+a}'), get_global_symbol_table()) == 3
    
    def test_interpret_simple_unary(self) -> None:
        assert interpret_module(p('-2'), get_global_symbol_table()) == -2
    
    def test_interpret_simple_unary_not(self) -> None:
        assert interpret_module(p('not true'), get_global_symbol_table()) == False

    def test_interpret_simple_reassignment(self) -> None:
        assert interpret_module(p('var x = 1;x+1'), get_global_symbol_table()) == 2

    def test_interpret_simple_reassignment_with_block(self) -> None:
        assert interpret_module(p('var x = 1;{x=x+1}'), get_global_symbol_table()) == 2
    
    def test_interpret_simple_while(self) -> None:
        assert interpret_module(p('var x = 1; while x<3 do {x=x+1}'), get_global_symbol_table()) == 3
    
    def test_interpret_simple_and(self) -> None:
        assert interpret_module(p('var some = false;var some_else = true;some and {some_else = false;true};some_else'), get_global_symbol_table()) == True

    def test_interpret_simple_or(self) -> None:
        assert interpret_module(p('var some = false;true or {some = true;true};some'), get_global_symbol_table()) == False