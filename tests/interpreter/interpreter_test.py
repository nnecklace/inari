import io
from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.interpreter import interpret_module
from compiler.types import get_global_symbol_table
from compiler.ast import Module

import unittest
import unittest.mock

def p(input: str) -> Module:
    return parse(tokenize(input))

class InterpreterTest(unittest.TestCase):
    def test_interpret_simple(self) -> None:
        assert interpret_module(p('1 + 2'), get_global_symbol_table()) == 3

    def test_interpret_simple_if(self) -> None:
        assert interpret_module(p('if 5 < 10 then 2*5'), get_global_symbol_table()) == 10

    def test_interpret_simple_if_else(self) -> None:
        assert interpret_module(p('if 5 < 2 then 2*5 else 6/2'), get_global_symbol_table()) == 3

    def test_interpret_simple_if_else2(self) -> None:
        assert interpret_module(p('var x = 5; if 5 <= x and x == 5 then 2*5 else 6/2'), get_global_symbol_table()) == 10

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
        assert interpret_module(p('var x = 1; while x<3 do {x=x+1}; x'), get_global_symbol_table()) == 3
    
    def test_interpret_simple_and(self) -> None:
        assert interpret_module(p('var some = false;var some_else = true;some and {some_else = false;true};some_else'), get_global_symbol_table()) == True

    def test_interpret_simple_or(self) -> None:
        assert interpret_module(p('var some = false;true or {some = true;true};some'), get_global_symbol_table()) == False

    def test_interpret_simple_program(self) -> None:
        assert interpret_module(p('var n = 10; while n > 1 do { if n % 2 == 0 then { n = n / 2; } else { n = 3*n + 1; } } n'), get_global_symbol_table()) == 1

    def test_interpret_simple_program2(self) -> None:
        assert interpret_module(p('var n = 10; while n > 1 do { if n % 2 == 0 then { n = n / 2; } else { n = 3*n + 1; } } n'), get_global_symbol_table()) == 1

    def test_interpret_simple_program3(self) -> None:
        assert interpret_module(p('var x = { var y = 1; var z = 5; if z-y >= 1 then z else y }; x'), get_global_symbol_table()) == 5

    def test_interpret_simple_program4(self) -> None:
        assert interpret_module(p('var x = 10; var y = 10+x; while y > 0 do { y = y-1; }; y'), get_global_symbol_table()) == 0

    def test_interpret_simple_program5(self) -> None:
        assert interpret_module(p('if { var x = 2; var y = true; var z = 3; while x != z do { x = x+1 }; y } then 1 else 2'), get_global_symbol_table()) == 1

    def test_interpret_simple_program6(self) -> None:
        assert interpret_module(p('var x = 10; while x >= 1 do { var y = 100; while y >= 10 do { y = y - 1; } x = x - 1 }; x'), get_global_symbol_table()) == 0

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_interpret_simple_func_call(self, mock_stdout: io.StringIO) -> None:
        interpret_module(p('print_int(1)'), get_global_symbol_table())
        self.assertEqual(mock_stdout.getvalue(), '1\n')

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_interpret_simple_func_call_bool(self, mock_stdout: io.StringIO) -> None:
        interpret_module(p('print_bool(true)'), get_global_symbol_table())
        self.assertEqual(mock_stdout.getvalue(), 'True\n')

    def test_func_fails_with_wrong_arg_amount(self) -> None:
        self.assertRaises(Exception, interpret_module, p('print_bool(true, 2)'), get_global_symbol_table())

    def test_func_fails_with_wrong_arg_amount2(self) -> None:
        self.assertRaises(Exception, interpret_module, p('read_int(2)'), get_global_symbol_table())