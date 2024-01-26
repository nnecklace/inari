import re
from compiler.token import Token
from compiler.location import Location

# Regexes
regexes = {
    "comment": re.compile(r'(/{2,}|#|;{2,}).*'),
    "whitespace": re.compile(r'\s'),
    "number": re.compile(r'[0-9]*'),
    "identifier": re.compile(r'(^[^0-9]([a-z]|_))([a-z]|\d|_)*'),
    "non_negative_number": re.compile(r'[^-]?[0-9]'),
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

def tokenize_type(key: str, type: str, segment: str) -> list[tuple[int, int, str, str]]:
    return [(match.start(), match.end(), match.group(), type) for match in regexes[key].finditer(segment)]

def tokenize(source_code: str) -> list[Token]:
    tokens = []
    for line_num, line in enumerate(source_code.splitlines()):
        line = regexes['comment'].sub('', line).strip() # just remove all comments from each line

        if not line:
            continue

        matched_tokens = sorted(
            tokenize_type('identifier', 'identifier', line) +
            tokenize_type('non_negative_number', 'int_literal', line) + 
            tokenize_type('operator', 'operator', line) +
            tokenize_type('punctuation', 'punctuation', line) +
            tokenize_type('whitespace', 'whitespace', line)
        )

        matched_str = ''.join([token[2] if token else '' for token in matched_tokens])

        err = re.compile(r'[^{}]'.format(re.escape(matched_str))).search(line)

        if err:
            raise ValueError(f'Unidentified pattern in line: {line} character: {line[err.start()]}\n{(line+'\n')+''.join([' ' for _ in range(err.start())])}^')

        for match in matched_tokens:
            if match and match[3] != 'whitespace':
                tokens.append(create_token(match[2], match[3], '', line_num, match[0]))

    return tokens