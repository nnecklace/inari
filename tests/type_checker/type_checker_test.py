from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.type_checker import typecheck_module
from compiler.types import FunctionSignature, Int, Bool, Pointer, Unit, Type, get_global_symbol_table_types
from compiler.ast import Module, Expression

import unittest

def p(input: str) -> Module:
    return parse(tokenize(input))

def find(expr: Expression, exprs: list[tuple[Expression, Type]]) -> Type:
    for exp in exprs:
        if exp[0] == expr:
            return exp[1]
    return Unit 

# TODO: Add more tests
class TypeCheckerTest(unittest.TestCase):
    def test_typecheck_simple_literal_positive_int(self):
        expr = p('1')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Int
    
    def test_typecheck_simple_literal_bool(self):
        expr = p('true')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Bool

    def test_typecheck_simple_literal_negative_int(self):
        expr = p('-2')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Int 

    def test_typecheck_simple_binary_op(self):
        expr = p('2+2')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Int 

    def test_typecheck_simple_var(self):
        sym = get_global_symbol_table_types()
        typecheck_module(p('var a = true'), sym)
        assert sym.bindings['a'] == Bool
    
    def test_typecheck_simple_block(self):
        expr = p('{2+1}')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Int 

    def test_typecheck_simple_block_with_2_expressions(self):
        expr = p('{2+1;true}')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Bool 

    def test_typecheck_simple_block_with_vars(self):
        expr = p('{var a = 2+1;true;a}')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Int 

    def test_typecheck_simple_block_unit(self):
        expr = p('{var a = 2+1;true;a;}')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Unit

    def test_typecheck_simple_while(self):
        expr = p('while true do 1 + 1')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Int # TODO: check spec, should probably return unit

    def test_typecheck_simple_if_then(self):
        expr = p('if true then 1 + 1')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Int 

    def test_typecheck_simple_if_then_else(self):
        expr = p('if true then 1 + 1 else 3')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Int 

    def test_typecheck_simple_function_call(self):
        expr = p('print_int(1)')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Unit 

    def test_typecheck_simple_var_with_type(self):
        sym = get_global_symbol_table_types()
        typecheck_module(p('var a: Bool = true'), sym)
        assert sym.bindings['a'] == Bool

    def test_typecheck_var_with_same_name_as_type(self):
        sym = get_global_symbol_table_types()
        typecheck_module(p('var Bool: Int = 1'), sym)
        assert sym.bindings['Bool'] == Int

    def test_typecheck_function_definition(self):
        expr = p('fun test(): Int {1}')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == FunctionSignature([], Int)

    def test_typecheck_function_definition_with_args(self):
        expr = p('fun test(x: Int, y: Bool, z: Unit): Int {1}')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == FunctionSignature([Int, Bool, Unit], Int)

    def test_typecheck_unary_pointers(self):
        pointer = Pointer()
        pointer.value = Int
        expr = p('var x: Int = 1; var y: Int* = &x; y')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[2], expr_types) == pointer

    def test_typecheck_unary_pointer_to_pointer(self):
        pointer = Pointer()
        pointer.value = Pointer()
        pointer.value.value = Int
        expr = p('var x: Int = 1; var y: Int* = &x; var z: Int** = &y; z')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[3], expr_types) == pointer

    def test_typecheck_unary_pointer_dereference(self):
        expr = p('var x: Int = 1; var y: Int* = &x; var z: Int = *y; z')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[3], expr_types) == Int

    def test_typecheck_unary_pointer_dereference_to_pointer(self):
        pointer = Pointer()
        pointer.value = Int
        expr = p('var x: Int = 1; var y: Int* = &x; var z: Int** = &y; var n: Int* = *z; n')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[4], expr_types) == pointer

    # TODO: var x: Int = 1; var y: Int* = &x; var z: Int** = &y; var n: Int = **z; n

    # TODO: Add tests for function calls with params for custom functions

    def test_typecheck_function_definition_with_args(self):
        self.assertRaises(Exception, typecheck_module, p('fun test(x: Int, y: Bool, z: Unit): Int {true}'), get_global_symbol_table_types())

    def test_typecheck_simple_var_with_error_type(self):
        self.assertRaises(Exception, typecheck_module, p('var test: Int = true'), get_global_symbol_table_types())

    def test_typecheck_simple_while_error_cond(self):
        self.assertRaises(Exception, typecheck_module, p('while 1 do 1 + 1'), get_global_symbol_table_types())

    def test_typecheck_simple_if_error_cond(self):
        self.assertRaises(Exception, typecheck_module, p('if 1 then 1 + 1'), get_global_symbol_table_types())

    def test_typecheck_simple_if_error_branches(self):
        self.assertRaises(Exception, typecheck_module, p('if true then 1 + 1 else false'), get_global_symbol_table_types())

    def test_typecheck_simple_binary_op_error(self):
        self.assertRaises(Exception, typecheck_module, p('2+true'), get_global_symbol_table_types())