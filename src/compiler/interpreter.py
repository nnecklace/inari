from typing import Any, Dict
from compiler.ast import Expression, Literal, IfThenElse, While, BinaryOp, Var

from dataclasses import dataclass
type Value = int | bool | None

@dataclass
class SymbolTable:
    bindings: Dict[str, Expression]
    parent: Any

def interpret(node: Expression, symbol_table: SymbolTable) -> Value:
    match node:
        case Literal():
            return node.value

        case BinaryOp():
            a: Any = interpret(node.left, SymbolTable(bindings={}, parent=symbol_table))
            b: Any = interpret(node.right, SymbolTable(bindings={}, parent=symbol_table))
            match node.op:
                case '+':
                    return a + b
                case '<':
                    return a < b
                case '-':
                    return a-b
                case '*':
                    return a*b
                case '/':
                    return a/b
                case '>':
                    return a>b
                case '<=':
                    return a<=b
                case '>=':
                    return a>=b
                case '%':
                    return a%b
                case '==':
                    return a==b
                case '!=':
                    return a != b
                case _:
                    raise Exception(f'Unknown operator {node.op}')

        case IfThenElse():
            if interpret(node.cond, SymbolTable(bindings={}, parent=symbol_table)):
                return interpret(node.then, SymbolTable(bindings={}, parent=symbol_table))
            else:
                return interpret(node.otherwise, SymbolTable(bindings={}, parent=symbol_table))

        case Var():
            symbol_table.bindings[node.name.name] = interpret(node.initialization, SymbolTable(bindings={}, parent=symbol_table))
            return None
