import re
from compiler.token import Token
from compiler.location import Location

# Regexes
regexes = {
    "comment": re.compile(r'(/{2,}|#|;{2,}).*'),
    "whitespace": re.compile(r'\s'),
    "number": re.compile(r'[0-9]*'),
    "identifier": re.compile(r'\b[a-z_][a-z0-9_]*\b'),
    "int_literal": re.compile(r'[^-]?[0-9]'),
    "operator": re.compile(r'(\+|-|\*|/|==|!=|<=|=>|>|<|=)'),
    "punctuation": re.compile(r'(\(|\)|{|}|,|;)')
}

def create_token(
        token: str,
        type: str, 
        file: str, 
        line: int,
        column: int
) -> Token:
    return Token(text=token, type=type, location=Location(file=file, line=line, column=column))

def find_token(type: str, segment: str) -> list[tuple[int, int, str, str]]:
    return [{'start': match.start(), 'end': match.end(), 'group': match.group(), 'type': type} for match in regexes[type].finditer(segment)]

def tokenize(source_code: str) -> list[Token]:
    tokens = []
    for line_num, line in enumerate(source_code.splitlines()):
        line = regexes['comment'].sub('', line).strip() # just remove all comments from each line

        if not line:
            continue

        matched_tokens = sorted(
            find_token('identifier', line) +
            find_token('int_literal', line) +
            find_token('operator', line) +
            find_token('punctuation', line) +
            find_token('whitespace', line),
        key=lambda token: token['start'])

        matched_str = ''.join([token['group'] if token else '' for token in matched_tokens])

        err = re.compile(r'[^{}]'.format(re.escape(matched_str))).search(line)

        if err:
            raise ValueError(f'Unidentified pattern in line: {line} character: {line[err.start()]}\n{(line+'\n')+''.join([' ' for _ in range(err.start())])}^')

        for match in matched_tokens:
            if match and match['type'] != 'whitespace':
                tokens.append(
                    Token(
                        text=match['group'], 
                        type=match['type'], 
                        location=Location(
                            file='',
                            line=line_num, 
                            column=match['start']
                        )
                    )
                )

    return tokens