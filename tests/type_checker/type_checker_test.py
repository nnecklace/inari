from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.type_checker import typecheck
from compiler.types import Int, Bool, Unit, Type, get_global_symbol_table_types
from compiler.ast import Expression

import unittest

def p(input: str) -> Expression:
    return parse(tokenize(input))

# TODO: Add more tests
class TypeCheckerTest(unittest.TestCase):
    def test_typecheck_simple_literal_positive_int(self):
        assert typecheck(p('1'), get_global_symbol_table_types()) == Int
    
    def test_typecheck_simple_literal_bool(self):
        assert typecheck(p('true'), get_global_symbol_table_types()) == Bool

    def test_typecheck_simple_literal_negative_int(self):
        assert typecheck(p('-2'), get_global_symbol_table_types()) == Int

    def test_typecheck_simple_binary_op(self):
        assert typecheck(p('2+2'), get_global_symbol_table_types()) == Int

    def test_typecheck_simple_var(self):
        sym = get_global_symbol_table_types()
        typecheck(p('var a = true'), sym)
        assert sym.bindings['a'] == Bool
    
    def test_typecheck_simple_block(self):
        assert typecheck(p('{2+1}'), get_global_symbol_table_types()) == Int

    def test_typecheck_simple_block_with_2_expressions(self):
        assert typecheck(p('{2+1;true}'), get_global_symbol_table_types()) == Bool

    def test_typecheck_simple_block_with_vars(self):
        assert typecheck(p('{var a = 2+1;true;a}'), get_global_symbol_table_types()) == Int

    def test_typecheck_simple_block_unit(self):
        assert typecheck(p('{var a = 2+1;true;a;}'), get_global_symbol_table_types()) == Unit

    def test_typecheck_simple_while(self):
        assert typecheck(p('while true do 1 + 1'), get_global_symbol_table_types()) == Int

    def test_typecheck_simple_if_then(self):
        assert typecheck(p('if true then 1 + 1'), get_global_symbol_table_types()) == Int

    def test_typecheck_simple_if_then_else(self):
        assert typecheck(p('if true then 1 + 1 else 3'), get_global_symbol_table_types()) == Int

    def test_typecheck_simple_function_call(self):
        assert typecheck(p('print_int(1)'), get_global_symbol_table_types()) == Unit

    def test_typecheck_simple_var_with_type(self):
        sym = get_global_symbol_table_types()
        typecheck(p('var a: Bool = true'), sym)
        assert sym.bindings['a'] == Bool

    def test_typecheck_var_with_same_name_as_type(self):
        sym = get_global_symbol_table_types()
        typecheck(p('var Bool: Int = 1'), sym)
        assert sym.bindings['Bool'] == Int

    def test_typecheck_simple_var_with_error_type(self):
        self.assertRaises(Exception, typecheck, p('var test: Int = true'), get_global_symbol_table_types())

    def test_typecheck_simple_while_error_cond(self):
        self.assertRaises(Exception, typecheck, p('while 1 do 1 + 1'), get_global_symbol_table_types())

    def test_typecheck_simple_if_error_cond(self):
        self.assertRaises(Exception, typecheck, p('if 1 then 1 + 1'), get_global_symbol_table_types())

    def test_typecheck_simple_if_error_branches(self):
        self.assertRaises(Exception, typecheck, p('if true then 1 + 1 else false'), get_global_symbol_table_types())

    def test_typecheck_simple_binary_op_error(self):
        self.assertRaises(Exception, typecheck, p('2+true'), get_global_symbol_table_types())