from typing import Any, Dict, Callable, Generic, TypeVar
from typing_extensions import Self

type Int = int # type: ignore[valid-type]
type Bool = bool # type: ignore[valid-type]
type Unit = None # type: ignore[valid-type]
type Unknown = None # type: ignore[valid-type]

T = TypeVar('T')

type PrimitiveType = Int | Bool | Unit | Unknow # type: ignore[valid-type]n

class FunctionDefinition():
    arguments: list[PrimitiveType]
    return_type: PrimitiveType

    def __init__(self: Self, arguments: list[PrimitiveType], return_type: PrimitiveType) -> None:
        self.arguments = arguments
        self.return_type = return_type

    def __eq__(self: Self, other: object) -> bool:
        if not isinstance(other, FunctionDefinition):
            return NotImplemented

        if len(other.arguments) != len(self.arguments):
            return False

        for i, obj in enumerate(other.arguments):
            if obj != self.arguments[i]:
                return False

        return self.return_type == other.return_type

type Type = PrimitiveType | Callable | FunctionDefinition # type: ignore[valid-type]

type Value = int | bool | Callable | None # type: ignore[valid-type]

def get_type_from_str(type: str) -> Type: # type: ignore[valid-type]
    if type == 'Int':
        return Int
    if type == 'Bool':
        return Bool
    if type == 'Unit':
        return Unit
    
    return Unknown

class SymbolTable(Generic[T]):
    bindings: Dict[str, T]
    parent: Any
    def __init__(self: Self, bindings: Dict[str, T], parent: Any) -> None:
        self.bindings = bindings
        self.parent = parent

    def add_local(self: Self, key: str, value: T) -> None:
        self.bindings[key] = value
        
    def require(self: Any, name: str, new_value: Type = None) -> T: # type: ignore[valid-type]
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
    return SymbolTable[Type](bindings={ # type: ignore[valid-type]
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
        'read_int': Callable[[], Int]},
        parent=None)

def get_global_symbol_table() -> SymbolTable:
    return SymbolTable[Value](bindings={ # type: ignore[valid-type]
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
