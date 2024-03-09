from dataclasses import dataclass, field
from compiler.types import Type, Unit
from compiler.location import Location

@dataclass
class Expression:
    """Base class for AST nodes representing expressions."""
    # TODO: Add Location to expression
    type: Type = field(kw_only=True, default=Unit) # type: ignore[valid-type]
    location: Location = field(kw_only=True, default_factory=(lambda: Location(file='', line=0, column=0)))

@dataclass
class Module:
    namespace: str
    expressions: list[Expression]
    type: Type = field(kw_only=True, default=Unit)
    location: Location = field(kw_only=True, default_factory=(lambda: Location(file='', line=0, column=0)))

@dataclass
class Literal(Expression):
    value: int | bool | None
    # (value=None is used when parsing the keyword `unit`)
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Literal):
            return NotImplemented

        return self.value == other.value

@dataclass
class Identifier(Expression):
    name: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Identifier):
            return NotImplemented

        return self.name == other.name

@dataclass
class IfThenElse(Expression):
    """AST node for If then else operation like `if a then b else c`"""
    cond: Expression
    then: Expression
    otherwise: Expression | None = None
    name: str = 'if'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IfThenElse):
            return NotImplemented

        return self.cond == other.cond and self.then == other.then and self.otherwise == other.otherwise

@dataclass
class While(Expression):
    cond: Expression
    body: Expression
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, While):
            return NotImplemented

        return self.cond == other.cond and self.body == other.body

@dataclass
class Var(Expression):
    name: Identifier
    initialization: Expression
    declared_type: Type | None = None # type: ignore[valid-type]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Var):
            return NotImplemented

        return self.initialization == other.initialization and self.name == other.name

@dataclass
class FuncCall(Expression):
    args: list[Expression]
    name: Identifier

@dataclass
class Block(Expression):
    statements: list[Expression]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Block):
            return NotImplemented

        if len(other.statements) != len(self.statements):
            return False

        for i, obj in enumerate(other.statements):
            if obj != self.statements[i]:
                return False

        return True

@dataclass
class Argument(Identifier):
    declared_type: Type | None = None # type: ignore[valid-type]

@dataclass
class FuncDef(Expression):
    name: Identifier
    args: list[Argument]
    body: Block
    declared_type: Type | None = None # type: ignore[valid-type]

@dataclass
class UnaryOp(Expression):
    """AST node for unary operator like `not -1`"""
    op: str
    right: Expression

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UnaryOp):
            return NotImplemented
        
        return self.op == other.op and self.right == other.right

@dataclass
class BinaryOp(Expression):
    """AST node for a binary operation like `A + B`"""
    left: Expression
    op: str
    right: Expression

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BinaryOp):
            return NotImplemented

        return self.left == other.left and \
               self.right == other.right and \
               self.op == other.op

@dataclass
class BreakContinue(Expression):
    name: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BreakContinue):
            return NotImplemented

        return self.name == other.name