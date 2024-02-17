from dataclasses import dataclass

@dataclass
class Expression:
    """Base class for AST nodes representing expressions."""
    # TODO: Add Location to expression

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
    otherwise: Expression = None
    name: str = 'if'

@dataclass
class While(Expression):
    cond: Expression
    body: Expression

@dataclass
class Var(Expression):
    name: Identifier
    initialization: Expression

@dataclass
class FuncCall(Expression):
    """AST node for function calls"""
    args: list[Expression]
    name: str

@dataclass
class Block(Expression):
    """AST node to represent blocks"""
    statements: list[Expression]

    ended_with_semi_colon: bool = False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Block):
            return NotImplemented

        for obj in other.statements:
            if obj not in self.statements:
                return False

        return True

@dataclass
class UnaryOp(Expression):
    """AST node for unary operator like `not -1`"""
    op: str
    right: Expression

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