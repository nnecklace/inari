import regex as re
from compiler.token import Token
from compiler.location import Location

# Regexes
regexes = {
    "comment": re.compile(r'(/{2,}|#).*'),
    "whitespace": re.compile(r'\s'),
    "number": re.compile(r'[0-9]*'),
    "identifier": re.compile(r'\b[a-z_][a-z0-9_]*\b(?<!\btrue|\bfalse)'),
    "int_literal": re.compile(r'\d+'),
    "bool_literal": re.compile(r'\b(true|false)'), # check this
    "operator": re.compile(r'(\+|-|%|\*|/|==|!=|<=|>=|>|<|=)'),
    "punctuation": re.compile(r'(\(|\)|{|}|,|;)')
}

def find_token(type: str, segment: str) -> list[tuple[int, int, str, str]]:
    return [{'start': match.start(), 'end': match.end(), 'group': match.group(), 'type': type} for match in regexes[type].finditer(segment)]

def tokenize(source_code: str) -> list[Token]:
    tokens = [Token( text='{', type='punctuation', location=Location('', 0, 0), meta='start')]

    for line_num, line in enumerate(source_code.splitlines()):
        line = regexes['comment'].sub('', line).strip() # just remove all comments from each line

        if not line:
            continue

        matched_tokens = sorted(
            find_token('int_literal', line) +
            find_token('bool_literal', line) +
            find_token('identifier', line) +
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

    tokens.append(Token(text='}', type='punctuation', location=Location('', tokens[-1].location.line+1, tokens[-1].location.column+1), meta='end'))

    return tokens