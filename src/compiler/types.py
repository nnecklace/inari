from typing import Any, Dict, Callable, Generic, TypeVar, Union, Optional
from typing_extensions import Self

type Int = int # type: ignore[valid-type]
type Bool = bool # type: ignore[valid-type]
type Unit = None # type: ignore[valid-type]
type Unknown = None # type: ignore[valid-type]

T = TypeVar('T')

type PrimitiveType = Union[Int, Bool, Unit, Unknown] # type: ignore[valid-type]

class Pointer:
    value: Union['Pointer', PrimitiveType] = Unit

    def __eq__(self: Self, other: object) -> bool:
        if not isinstance(other, Pointer):
            return NotImplemented

        t = self
        t_levels = 0
        while type(t) != type(PrimitiveType):
            t_levels += 1
            t = t.value # type: ignore[assignment]

        o = other
        o_levels = 0
        while type(o) != type(PrimitiveType):
            o_levels += 1
            o = o.value # type: ignore[assignment]

        return o_levels == t_levels and o is t

class FunctionSignature():
    arguments: list[PrimitiveType]
    return_type: PrimitiveType | Pointer

    def __init__(self: Self, arguments: list[PrimitiveType], return_type: PrimitiveType | Pointer) -> None:
        self.arguments = arguments
        self.return_type = return_type

    def __eq__(self: Self, other: object) -> bool:
        if not isinstance(other, FunctionSignature):
            return NotImplemented

        if len(other.arguments) != len(self.arguments):
            return False

        for i, obj in enumerate(other.arguments):
            if obj != self.arguments[i]:
                return False

        return self.return_type == other.return_type

# This part has to be duplicated because python doesn't understand nested unions well
Type = Union[Int, Bool, Unit, FunctionSignature, Pointer] # type: ignore[valid-type]

type Value = int | bool | Callable | None # type: ignore[valid-type]

def get_type_from_str(type: str) -> Type: # type: ignore[valid-type]
    pointers = type.count('*')
    type = type.split('*')[0]

    # python doesn't like when variables change type, but hey it allows it so I use it :)

    if type == 'Int':
        type = Int # type: ignore[assignment]
    elif type == 'Bool':
        type = Bool # type: ignore[assignment]
    elif type == 'Unit':
        type = Unit # type: ignore[assignment]
    else:
        type = Unknown # type: ignore[assignment]

    if pointers  == 0 or type is Unknown:
        return type 

    top_pointer = pointer = Pointer()
    for _ in range(pointers-1):
        pointer.value = Pointer()
        pointer = pointer.value
    pointer.value = type
    return top_pointer

class SymbolTable(Generic[T]):
    bindings: Dict[str, T]
    parent: Optional['SymbolTable[T]']
    def __init__(self: Self, bindings: Dict[str, T], parent: Optional['SymbolTable[T]']) -> None:
        self.bindings = bindings
        self.parent = parent

    def add_local(self: Self, key: str, value: T) -> None:
        self.bindings[key] = value
        
    def require(self: Self, name: str, new_value: Type = None) -> T: # type: ignore[valid-type]
        current = self
        while current:
            if name in current.bindings:
                if new_value is not None:
                    current.bindings[name] = new_value # type: ignore[assignment]
                return current.bindings[name]
            else:
                current = current.parent # type: ignore[assignment]
        
        raise Exception(f'No symbol {name} found')

def get_global_symbol_table_types() -> SymbolTable[Type]:
    return SymbolTable[Type](bindings={ # type: ignore[valid-type]
        'unary_-': FunctionSignature([Int], Int), # type: ignore[list-item]
        'unary_not':FunctionSignature([Bool], Bool), # type: ignore[list-item]
        'unary_*': FunctionSignature([Pointer], Type), # type: ignore[list-item]
        'unary_&': FunctionSignature([Type], Pointer), # type: ignore[list-item]
        '+': FunctionSignature([Int,Int], Int), # type: ignore[list-item]
        '-': FunctionSignature([Int,Int], Int), # type: ignore[list-item]
        '*': FunctionSignature([Int,Int], Int), # type: ignore[list-item]
        '/': FunctionSignature([Int,Int], Int), # type: ignore[list-item]
        '%': FunctionSignature([Int,Int], Int), # type: ignore[list-item]
        '<': FunctionSignature([Int,Int], Bool), # type: ignore[list-item]
        '>': FunctionSignature([Int,Int], Bool), # type: ignore[list-item]
        '<=': FunctionSignature([Int,Int], Bool), # type: ignore[list-item]
        '>=': FunctionSignature([Int,Int], Bool), # type: ignore[list-item]
        'and': FunctionSignature([Bool,Bool], Bool), # type: ignore[list-item]
        'or': FunctionSignature([Bool,Bool], Bool), # type: ignore[list-item]
        'print_int': FunctionSignature([Int], Unit), # type: ignore[list-item]
        'print_bool': FunctionSignature([Bool], Unit), # type: ignore[list-item]
        'read_int': FunctionSignature([], Int)},
        parent=None)

def get_global_symbol_table() -> SymbolTable[Value]:
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
