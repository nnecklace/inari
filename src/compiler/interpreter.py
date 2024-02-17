from typing import Any, Dict, Callable
from compiler.ast import Expression, Literal, IfThenElse, While, BinaryOp, Var, Block, Identifier, UnaryOp, FuncCall

type Value = int | bool | Callable | None

class SymbolTable:
    bindings: Dict[str, Value]
    parent: Any # should be SymbolTable but python wants me to do some weird stupid shit that I don't feel like doing, so we put Any here instead
    def __init__(self, bindings, parent):
        self.bindings = bindings
        self.parent = parent

top_level_symbol_table = SymbolTable(bindings={
    'unary_-': lambda x: -x,
    'unary_not': lambda x: not x,
    '+': lambda x,y: x+y,
    '-': lambda x,y: x-y,
    '*': lambda x,y: x*y,
    '/': lambda x,y: x/y,
    '%': lambda x,y: x%y,
    '<': lambda x,y: x<y,
    '>': lambda x,y: x>y,
    '<=': lambda x,y: x<=y,
    '>=': lambda x,y: x>=y,
    '==': lambda x,y: x==y,
    '!=': lambda x,y: x!=y,
    'print_int': lambda x: print(int(x), end='\n'),
    'print_bool': lambda x: print(bool(x), end='\n'),
    'read_int': lambda: int(input())}, 
    parent=None)

def find_symbol(name: str, symbol_table: SymbolTable, new_value: Value = None):
    current = symbol_table
    while current:
        if name in current.bindings:
            if new_value:
                current.bindings[name] = new_value
            return current.bindings[name]
        else:
            current = current.parent
    
    raise Exception(f'No symbol {name} found')

def interpret(node: Expression, symbol_table: SymbolTable) -> Value:
    match node:
        case Literal():
            return node.value

        case FuncCall():
            func = find_symbol(node.name, symbol_table)
            interpreted_args = [interpret(arg, symbol_table) for arg in node.args]
            if node.name == 'print_int' or node.name == 'print_bool':
                if len(interpreted_args) != 1:
                    raise Exception(f'Function expects 1 argument, {len(interpreted_args)} given')
                else:
                    return func(interpreted_args[0])
            elif node.name == 'read_int':
                if len(interpreted_args) > 0:
                    raise Exception(f'Function expects 0 arguments, {len(interpreted_args)} given')
                else:
                    return func()
            else:
                return func(*interpreted_args)

        case Identifier():
            return find_symbol(node.name, symbol_table)

        case BinaryOp():
            if node.op == '=':
                return find_symbol(node.left.name, symbol_table, interpret(node.right, symbol_table))

            if node.op == 'and':
                return interpret(node.left, symbol_table) and interpret(node.right, symbol_table)

            if node.op == 'or':
                return interpret(node.left, symbol_table) or interpret(node.right, symbol_table)

            return find_symbol(node.op, symbol_table)(
                interpret(node.left, symbol_table),
                interpret(node.right, symbol_table)
            )

        case UnaryOp():
            return find_symbol('unary_'+node.op, symbol_table)(
                interpret(node.right, symbol_table)
            )

        case IfThenElse():
            if interpret(node.cond, symbol_table):
                return interpret(node.then, symbol_table)
            else:
                return interpret(node.otherwise, symbol_table)

        case While():
            last = None
            while interpret(node.cond, symbol_table):
                last = interpret(node.body, symbol_table)
            return last

        case Var():
            symbol_table.bindings[node.name.name] = interpret(node.initialization, symbol_table)
        
        case Block():
            new_symbol_table = SymbolTable(bindings={}, parent=symbol_table)

            for expr in node.statements[:len(node.statements)-1]:
                interpret(expr, new_symbol_table)

            return interpret(node.statements[-1], new_symbol_table)
