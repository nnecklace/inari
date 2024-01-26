from dataclasses import dataclass


@dataclass
class L:
    file: str
    line: int
    column: int

@dataclass
class Location:
    file: str
    line: int
    column: int