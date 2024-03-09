from compiler.ast import BreakContinue, Expression, BinaryOp, FuncDef, Literal, Identifier, UnaryOp, Var, Block, While, IfThenElse, FuncCall, Module
from compiler.types import FunctionSignature, Int, Type, Bool, Unit, SymbolTable, Value
from typing import Any, Callable, Dict, get_args

def get_type(value: Value) -> Type: # type: ignore[valid-type]
    if value is int:
        return Int
    if value is bool:
        return Bool

    return Unit

def args_match(arg_types: list[Type], args: list[Type]) -> bool: # type: ignore[valid-type]
    for indx, arg in enumerate(args):
        if arg is not arg_types[indx]:
            return False
    
    return True

def type_check_function(func: FunctionSignature, arguments: list[Expression], symbol_table: SymbolTable) -> Any:
    passed_args = [typecheck(arg, symbol_table) for arg in arguments]
    if args_match(func.arguments, passed_args):
        return func.return_type
    else:
        raise Exception(f'Argument missmatch for function expecting arguments with types {[func.arguments]} got {passed_args}')

def return_and_assign(node: Expression, type: Type) -> Type: # type: ignore[valid-type]
    node.type = type
    return type

def typecheck_module(module: Module, root_table: SymbolTable) -> list[tuple[Expression, Type]]:
    expr_types: list[tuple[Expression, Type]] = []
    for expr in module.expressions:
        expr_types.append((expr, typecheck(expr, root_table)))

    return expr_types

def typecheck(node: Expression, symbol_table: SymbolTable) -> Type: # type: ignore[valid-type]
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
                type_check_function(symbol_table.require('unary_'+node.op), [node.right], symbol_table)
            )

        case FuncDef():
            t = node.declared_type
            body = typecheck(node.body, symbol_table)

            if not t:
                t = Unit

            if t is not body:
                raise Exception(f'Function {node.name} return type must be same as given type, mismatch {t} =/= {body}')

            args = [arg.declared_type for arg in node.args]

            for arg in node.args:
                symbol_table.add_local(f'{node.name}_{arg.name}', arg.declared_type)

            func_def = FunctionSignature(args, t)

            symbol_table.add_local(node.name.name, func_def)

            return return_and_assign(node, func_def)

        case FuncCall():
            return return_and_assign(
                node, 
                type_check_function(symbol_table.require(node.name), node.args, symbol_table)
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
                type_check_function(symbol_table.require(node.op), [node.left, node.right], symbol_table)
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
            variable_type = node.declared_type
            initialization_type = typecheck(node.initialization, symbol_table)
            if variable_type != None and variable_type is not initialization_type:
                raise Exception(f'Variable {node.name.name} declared type {variable_type} does not match with initialization {initialization_type}')
            
            symbol_table.add_local(node.name.name, initialization_type)

            return return_and_assign(node, initialization_type)
        
        case Block():
            new_symbol_table = SymbolTable[Type](bindings={}, parent=symbol_table) # type: ignore[valid-type]
            for expr in node.statements[:len(node.statements)-1]:
                typecheck(expr, new_symbol_table)
                
            # TODO: most likely fails with empty statement list, actually probably not but lets remember to check
            return return_and_assign(node, typecheck(node.statements[-1], new_symbol_table))
    
    raise Exception('Unknown expression type in type checker')