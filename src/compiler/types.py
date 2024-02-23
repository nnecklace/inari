from typing import Dict, Callable, Generic, TypeVar
from typing_extensions import Self

type Int = int
type Bool = bool
type Unit = None
type Unknown = None

type Type = Int | Bool | Callable | Unit | Unknown

type Value = int | bool | Callable | None

def get_type_from_str(type: str) -> Type:
    if type == 'Int':
        return Int
    if type == 'Bool':
        return Bool
    if type == 'Unit':
        return Unit
    
    return Unknown

T = TypeVar('T')

class SymbolTable(Generic[T]):
    bindings: Dict[str, T]
    parent: Self
    def __init__(self, bindings, parent):
        self.bindings = bindings
        self.parent = parent

    def add_local(self: Self, key: str, value: T):
        self.bindings[key] = value
        
    def require(self: Self, name: str, new_value: Type = None):
        current = self
        while current:
            if name in current.bindings:
                if new_value:
                    current.bindings[name] = new_value
                return current.bindings[name]
            else:
                current = current.parent
        
        raise Exception(f'No symbol {name} found')

def get_global_symbol_table_types() -> SymbolTable:
    return SymbolTable[Type](bindings={
        'unary_-': Callable[[Int], Int],
        'unary_not':Callable[[Bool], Bool],
        '+': Callable[[Int,Int], Int],
        '-': Callable[[Int,Int], Int],
        '*': Callable[[Int,Int], Int],
        '/': Callable[[Int,Int], Int],
        '%': Callable[[Int,Int], Int],
        '<': Callable[[Int,Int], Bool],
        '>': Callable[[Int,Int], Bool],
        '<=': Callable[[Int,Int], Bool],
        '>=': Callable[[Int,Int], Bool],
        '==': Callable[[Int,Int], Bool], # these should take any types
        '!=': Callable[[Int,Int], Bool], # these should take any types
        'and': Callable[[Bool,Bool], Bool],
        'or': Callable[[Bool,Bool], Bool],
        'print_int': Callable[[Int], Unit],
        'print_bool': Callable[[Bool], Unit],
        'read_int': Callable[[], Int]}, parent=None)

def get_global_symbol_table() -> SymbolTable:
    return SymbolTable[Value](bindings={
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
        'read_int': lambda: int(input())}, parent=None)
