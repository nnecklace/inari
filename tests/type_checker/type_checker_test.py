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
    def test_typecheck_simple_literal_positive_int(self) -> None:
        expr = p('1')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Int
    
    def test_typecheck_simple_literal_bool(self) -> None:
        expr = p('true')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Bool

    def test_typecheck_simple_literal_negative_int(self) -> None:
        expr = p('-2')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Int 

    def test_typecheck_simple_binary_op(self) -> None:
        expr = p('2+2')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Int 

    def test_typecheck_simple_var(self) -> None:
        sym = get_global_symbol_table_types()
        typecheck_module(p('var a = true'), sym)
        assert sym.bindings['a'] == Bool
    
    def test_typecheck_simple_block(self) -> None:
        expr = p('{2+1}')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Int 

    def test_typecheck_simple_block_with_2_expressions(self) -> None:
        expr = p('{2+1;true}')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Bool 

    def test_typecheck_simple_block_with_vars(self) -> None:
        expr = p('{var a = 2+1;true;a}')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Int 

    def test_typecheck_simple_block_unit(self) -> None:
        expr = p('{var a = 2+1;true;a;}')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Unit

    def test_typecheck_simple_while(self) -> None:
        expr = p('while true do 1 + 1')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Unit

    def test_typecheck_simple_if_then(self) -> None:
        expr = p('if true then 1 + 1')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Int 

    def test_typecheck_simple_if_then_else(self) -> None:
        expr = p('if true then 1 + 1 else 3')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Int 

    def test_typecheck_simple_function_call(self) -> None:
        expr = p('print_int(1)')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Unit 

    def test_typecheck_simple_function_call2(self) -> None:
        expr = p('print_bool(true)')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == Unit

    def test_typecheck_simple_function_call3(self) -> None:
        expr = p('var x: Int = read_int(); x')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[-1], expr_types) == Int

    def test_typecheck_simple_var_with_type(self) -> None:
        sym = get_global_symbol_table_types()
        typecheck_module(p('var a: Bool = true'), sym)
        assert sym.bindings['a'] == Bool

    def test_typecheck_var_with_same_name_as_type(self) -> None:
        sym = get_global_symbol_table_types()
        typecheck_module(p('var Bool: Int = 1'), sym)
        assert sym.bindings['Bool'] == Int

    def test_typecheck_function_definition(self) -> None:
        expr = p('fun test(): Int {1}')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == FunctionSignature([], Int)

    def test_typecheck_function_definition_with_args(self) -> None:
        expr = p('fun test(x: Int, y: Bool, z: Unit): Int {1}')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[0], expr_types) == FunctionSignature([Int, Bool, Unit], Int) # type: ignore[list-item]

    def test_typecheck_unary_pointers(self) -> None:
        pointer = Pointer()
        pointer.value = Int
        expr = p('var x: Int = 1; var y: Int* = &x; y')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[2], expr_types) == pointer

    def test_typecheck_unary_pointer_to_pointer(self) -> None:
        pointer = Pointer()
        pointer.value = Pointer()
        pointer.value.value = Int
        expr = p('var x: Int = 1; var y: Int* = &x; var z: Int** = &y; z')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[3], expr_types) == pointer

    def test_typecheck_unary_pointer_dereference(self) -> None:
        expr = p('var x: Int = 1; var y: Int* = &x; var z: Int = *y; z')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[-1], expr_types) == Int

    def test_typecheck_unary_pointer_dereference_to_pointer(self) -> None:
        pointer = Pointer()
        pointer.value = Int
        expr = p('var x: Int = 1; var y: Int* = &x; var z: Int** = &y; var n: Int* = *z; n')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[4], expr_types) == pointer

    def test_typecheck_unary_pointer_dereference_to_correct_type(self) -> None:
        expr = p('fun square(p: Int): Int { p = p * p } var x: Int = 3; square(x); x')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[-1], expr_types) == Int

    def test_typecheck_unary_pointer_dereference_to_correct_type_2(self) -> None:
        expr = p('fun square(p: Int*): Unit { *p = *p * *p; } var x: Int = 3; square(&x); x')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[-1], expr_types) == Int

    def test_typecheck_unary_pointer_dereference_nested(self) -> None:
        expr = p('var x: Int = 1; var y: Int* = &x; var z: Int** = &y; var n: Int = **z; n')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[-1], expr_types) == Int

    def test_typecheck_break_and_continue(self) -> None:
        expr = p('while true do { if true then break else continue }')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[-1], expr_types) == Unit

    def test_typecheck_equals(self) -> None:
        expr = p('var x: Bool = true; var y: Bool = false; x == y')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[-1], expr_types) == Bool

    def test_typecheck_equals_with_ints(self) -> None:
        expr = p('var x: Int = 1; var y: Int = 2; x == y')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[-1], expr_types) == Bool

    def test_typecheck_equals_with_wrong_types(self) -> None:
        self.assertRaises(Exception, typecheck_module, p('var x: Int = 1; var y: Bool = false; x == y'), get_global_symbol_table_types())

    def test_typecheck_not_equals(self) -> None:
        expr = p('var x: Bool = true; var y: Bool = false; x != y')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[-1], expr_types) == Bool

    def test_typecheck_not_equals_with_ints(self) -> None:
        expr = p('var x: Int = 1; var y: Int = 2; x != y')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[-1], expr_types) == Bool

    def test_typecheck_not_equals_with_wrong_types(self) -> None:
        self.assertRaises(Exception, typecheck_module, p('var x: Int = 1; var y: Bool = false; x != y'), get_global_symbol_table_types())

    def test_var_with_pointer_dereference_bool(self) -> None:
        expr = p('var x: Bool = true; var y: Bool* = &x; var z: Bool = *y; z')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[-1], expr_types) == Bool

    def test_var_with_pointer_dereference_many(self) -> None:
        pointer = Pointer()
        pointer.value = Bool
        expr = p('var x: Bool = true; var y: Bool* = &x; var z: Bool** = &y; var n: Bool* = *z; n')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[-1], expr_types) == pointer

    def test_typecheck_functions_get_unit(self) -> None:
        expr = p('fun square(p: Int*) { *p = *p * *p; } var x: Int = 3; square(&x); x')
        expr_types = typecheck_module(expr, get_global_symbol_table_types())
        assert find(expr.expressions[-1], expr_types) == Int

    def test_typecheck_custom_func_args(self) -> None:
        self.assertRaises(Exception, typecheck_module, p('fun f(x: Int*): Int { 1 + *x} f(true)'), get_global_symbol_table_types())

    def test_typecheck_reference_to_unit(self) -> None:
        self.assertRaises(Exception, typecheck_module, p('var x: Unit = {}; var y: Int* = &x;'), get_global_symbol_table_types())

    def test_typecheck_dereference_to_non_pointer(self) -> None:
        self.assertRaises(Exception, typecheck_module, p('var x: Int = 1; var y: Int = *x;'), get_global_symbol_table_types())

    def test_typecheck_pointer_types(self) -> None:
        self.assertRaises(Exception, typecheck_module, p('var x: Int = 1; var y: Bool* = &x; y'), get_global_symbol_table_types())

    def test_typecheck_function_definition_with_args2(self) -> None:
        self.assertRaises(Exception, typecheck_module, p('fun test(x: Int, y: Bool, z: Unit): Int {true}'), get_global_symbol_table_types())

    def test_typecheck_simple_var_with_error_type(self) -> None:
        self.assertRaises(Exception, typecheck_module, p('var test: Int = true'), get_global_symbol_table_types())

    def test_typecheck_simple_while_error_cond(self) -> None:
        self.assertRaises(Exception, typecheck_module, p('while 1 do 1 + 1'), get_global_symbol_table_types())

    def test_typecheck_simple_if_error_cond(self) -> None:
        self.assertRaises(Exception, typecheck_module, p('if 1 then 1 + 1'), get_global_symbol_table_types())

    def test_typecheck_simple_if_error_branches(self) -> None:
        self.assertRaises(Exception, typecheck_module, p('if true then 1 + 1 else false'), get_global_symbol_table_types())

    def test_typecheck_simple_binary_op_error(self) -> None:
        self.assertRaises(Exception, typecheck_module, p('2+true'), get_global_symbol_table_types())

    def test_typecheck_fails_no_symbol_found(self) -> None:
        self.assertRaises(Exception, typecheck_module, p('2+True'), get_global_symbol_table_types())