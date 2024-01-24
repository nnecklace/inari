import re

# Regexes
comment = re.compile(r'(/{2,}|#|;{2,}).*')
whitespace = re.compile(r'\s')
number = re.compile(r'[0-9]*')
identifier = re.compile(r'(\w|_)(\w|\d|_)*')

def tokenize(source_code: str) -> list[str]:
    tokens = []

    for line in source_code.splitlines():
        for segment in line.split():
            if comment.fullmatch(segment):
                break
            if whitespace.fullmatch(segment):
                continue

            if identifier.fullmatch(segment):
                tokens.append(segment)
            elif number.fullmatch(segment):
                tokens.append(segment)

    return tokens