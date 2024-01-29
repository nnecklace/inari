from dataclasses import dataclass

@dataclass
class Expression:
    """Base class for AST nodes representing expressions."""

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