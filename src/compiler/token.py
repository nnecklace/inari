from dataclasses import dataclass

from compiler.location import Location, L

@dataclass
class Token:
    text: str
    type: str
    location: Location | L

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return NotImplemented

        return (self.text == other.text and \
                self.type == other.type and \
                ((isinstance(other.location, L)) or \
                (self.location.file == other.location.file and \
                self.location.line == other.location.line and \
                self.location.column == other.location.column)))