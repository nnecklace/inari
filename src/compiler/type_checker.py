from inspect import isclass
from compiler.ast import BreakContinue, Expression, BinaryOp, FuncDef, Literal, Identifier, UnaryOp, Var, Block, While, IfThenElse, FuncCall, Module
from compiler.types import FunctionSignature, Int, Pointer, PrimitiveType, Type, Bool, Unit, SymbolTable, Value
from typing import Any, get_args

def get_type(value: Value) -> Type: # type: ignore[valid-type]
    if value is int:
        return Int
    if value is bool:
        return Bool

    return Unit

def args_match(arg_types: list[Type], args: list[Type]) -> bool: # type: ignore[valid-type]
    for indx, arg in enumerate(args):
        if arg_types[indx] is Type:
            if arg is not Int and arg is not Bool and not isinstance(arg, Pointer) and arg is not Pointer:
                return False
        elif arg_types[indx] is Pointer:
            if not isinstance(arg, Pointer):
                return False
        elif isinstance(arg_types[indx], Pointer):
            if not isinstance(arg, Pointer) or arg != arg_types[indx]:
                return False
        elif arg is not arg_types[indx]:
            return False
    
    return True

def type_check_function(name: str, func: FunctionSignature, arguments: list[Expression], symbol_table: SymbolTable) -> Any:
    passed_args = [typecheck(arg, symbol_table) for arg in arguments]
    if args_match(func.arguments, passed_args):
        if func.return_type is Pointer:
            # this is a hack to get pointers to work
            return_type = Pointer()
            return_type.value = passed_args[0]

            return return_type

        if func.return_type is Type and name == 'unary_*':
            # this is again a hack for pointers
            return_arg = passed_args[0]
            return return_arg.value

        return func.return_type
    else:
        raise Exception(f'Argument missmatch for function {name} expecting arguments with types {func.arguments} got {passed_args}')

def return_and_assign(node: Expression, type: Type) -> Type: # type: ignore[valid-type]
    node.type = type
    return type

def typecheck_module(module: Module, root_table: SymbolTable[Type]) -> list[tuple[Expression, Type]]:
    expr_types: list[tuple[Expression, Type]] = []
    fun_defs = [expr for expr in module.expressions if isinstance(expr, FuncDef)]
    
    # To allow for mutual recursion, we process the functions first briefly, later we check their bodies
    for f in fun_defs:
        args = [arg.declared_type for arg in f.args]
        t = f.declared_type
        if not t:
            t = Unit
        func_def = FunctionSignature(args, t)
        root_table.add_local(f.name.name, func_def)

    for expr in module.expressions:
        expr_types.append((expr, typecheck(expr, root_table)))

    return expr_types

def var_in_args(var_type: Type, expected_types: tuple[Any]) -> bool:
    for t in expected_types:
        if var_type is t or type(var_type) is t:
            return True

    return False

def typecheck(node: Expression, symbol_table: SymbolTable[Type]) -> Type: # type: ignore[valid-type]
    match node:
        case Literal():
            return return_and_assign(node, get_type(type(node.value)))

        case Identifier():
            return return_and_assign(node, symbol_table.require(node.name))

        case BreakContinue():
            return return_and_assign(node, Unit)

        case UnaryOp():
            return return_and_assign(
                node,
                type_check_function('unary_'+node.op, symbol_table.require('unary_'+node.op), [node.right], symbol_table)
            )

        case FuncDef():
            func = symbol_table.require(node.name.name)
            new_symbol_table = SymbolTable[Type](bindings={}, parent=symbol_table) # type: ignore[valid-type]
            for arg in node.args:
                new_symbol_table.add_local(arg.name, arg.declared_type)

            body = typecheck(node.body, new_symbol_table)

            if func.return_type is not body:
                raise Exception(f'Function {node.name} return type must be same as given type, mismatch {func.return_type} =/= {body}')

            return return_and_assign(node, func)

        case FuncCall():
            return return_and_assign(
                node, 
                type_check_function(node.name.name, symbol_table.require(node.name.name), node.args, symbol_table)
            )

        case BinaryOp():
            if node.op in ['=', '!=', '==']:
                left_type = typecheck(node.left, symbol_table)
                right_type = typecheck(node.right, symbol_table)
                if left_type is right_type:
                    if node.op == '=':
                        return return_and_assign(node, right_type)
                    else:
                        return return_and_assign(node, Bool)
                else:
                    raise Exception(f'Operator {node.op} expects the type of the right hand side to match the type {right_type} of the left hand side type {left_type}') 

            return return_and_assign(
                node, 
                type_check_function(node.op,symbol_table.require(node.op), [node.left, node.right], symbol_table)
            )

        case IfThenElse():
            cond = typecheck(node.cond, symbol_table)
            if cond is not Bool:
                raise Exception(f'If condition should be bool {cond} given')
            
            then = typecheck(node.then, symbol_table)

            if node.otherwise:
                otherwise = typecheck(node.otherwise, symbol_table)
                if then is not otherwise:
                    raise Exception(f'Then {then} and Else {otherwise} branch mismatched types')
            
            return return_and_assign(node, then)
        
        case While():
            cond = typecheck(node.cond, symbol_table)
            if cond is not Bool:
                raise Exception(f'While condition should be bool {cond} given')
            
            return return_and_assign(node, typecheck(node.body, symbol_table))

        case Var():
            # TODO: Clean this up
            variable_type = node.declared_type
            initialization_type = typecheck(node.initialization, symbol_table)
            if (initialization_type is Type and not var_in_args(variable_type, get_args(initialization_type))) or\
               (initialization_type is not Type and variable_type != None and ((variable_type is not initialization_type) and (variable_type != initialization_type))):
                    raise Exception(f'Variable {node.name.name} declared type {variable_type} does not match with initialization {initialization_type}')
            
            if (initialization_type is Type and var_in_args(variable_type, get_args(initialization_type))):
               symbol_table.add_local(node.name.name, variable_type)
            else:
               symbol_table.add_local(node.name.name, initialization_type)

            return return_and_assign(node, initialization_type)
        
        case Block():
            new_symbol_table = SymbolTable[Type](bindings={}, parent=symbol_table) # type: ignore[valid-type]
            for expr in node.statements[:len(node.statements)-1]:
                typecheck(expr, new_symbol_table)
                
            # TODO: most likely fails with empty statement list, actually probably not but lets remember to check
            return return_and_assign(node, typecheck(node.statements[-1], new_symbol_table))
    
    raise Exception('Unknown expression type in type checker')