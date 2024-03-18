from compiler.ast import Expression, Literal, IfThenElse, Module, While, BinaryOp, Var, Block, Identifier, UnaryOp, FuncCall
from compiler.types import SymbolTable, Unit, Value

def interpret_module(module: Module, root_table: SymbolTable) -> Value:
    for expr in module.expressions[:len(module.expressions)-1]:
        interpret(expr, root_table)

    return interpret(module.expressions[-1], root_table)

def interpret(node: Expression, symbol_table: SymbolTable) -> Value:
    match node:
        case Literal():
            return node.value

        case FuncCall():
            func = symbol_table.require(node.name.name)
            interpreted_args = [interpret(arg, symbol_table) for arg in node.args]
            if node.name.name == 'print_int' or node.name.name == 'print_bool':
                if len(interpreted_args) != 1:
                    raise Exception(f'Function expects 1 argument, {len(interpreted_args)} given')
                else:
                    return func(interpreted_args[0])
            elif node.name.name == 'read_int':
                if len(interpreted_args) > 0:
                    raise Exception(f'Function expects 0 arguments, {len(interpreted_args)} given')
                else:
                    return func()
            else:
                return func(*interpreted_args)

        case Identifier():
            return symbol_table.require(node.name)

        case BinaryOp():
            if node.op == '=':
                return symbol_table.require(node.left.name, interpret(node.right, symbol_table)) # type: ignore[attr-defined]

            if node.op == 'and':
                return interpret(node.left, symbol_table) and interpret(node.right, symbol_table)

            if node.op == 'or':
                return interpret(node.left, symbol_table) or interpret(node.right, symbol_table)

            return symbol_table.require(node.op)(
                interpret(node.left, symbol_table),
                interpret(node.right, symbol_table)
            )

        case UnaryOp():
            return symbol_table.require('unary_'+node.op)(
                interpret(node.right, symbol_table)
            )

        case IfThenElse():
            if interpret(node.cond, symbol_table):
                return interpret(node.then, symbol_table)
            else:
                if node.otherwise:
                    return interpret(node.otherwise, symbol_table)

        case While():
            last = None
            while interpret(node.cond, symbol_table):
                last = interpret(node.body, symbol_table)
            return last

        case Var():
            symbol_table.add_local(node.name.name, interpret(node.initialization, symbol_table))
        
        case Block():
            new_symbol_table = SymbolTable(bindings={}, parent=symbol_table)

            for expr in node.statements[:len(node.statements)-1]:
                interpret(expr, new_symbol_table)

            return interpret(node.statements[-1], new_symbol_table)

    return None