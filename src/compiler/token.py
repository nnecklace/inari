from dataclasses import dataclass

from compiler.location import Location, L

@dataclass
class Token:
    text: str
    type: str
    location: Location | L
    meta: str = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return NotImplemented

        return (self.text == other.text and \
                self.type == other.type and \
                (self.location.file == other.location.file and \
                self.location.line == other.location.line and \
                self.location.column == other.location.column) or \
                (type(other.location) == L))