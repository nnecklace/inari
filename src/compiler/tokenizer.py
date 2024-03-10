from functools import reduce
from typing import Dict
import regex as re # type: ignore[import-untyped]
from compiler.token import Token
from compiler.location import Location

# Regexes
regexes = {
    "comment": re.compile(r'(/{2,}|#).*'),
    "whitespace": re.compile(r'\s'),
    "identifier": re.compile(r'\b[A-Za-z_][A-Za-z0-9_]*\b(?<!\btrue|\bfalse|\band|\bor)'),
    "int_literal": re.compile(r'\b\d+\b'),
    "bool_literal": re.compile(r'\b(true|false)'),
    "operator": re.compile(r'(\+|-|%|\*|/|==|!=|<=|>=|>|<|=|\band|\bor)'),
    "punctuation": re.compile(r'(\(|\)|{|}|,|;|:)')
}

def find_token(type: str, segment: str) -> list[Dict[str, str]]:
    return [{'start': match.start(), 'end': match.end(), 'group': match.group(), 'type': type} for match in regexes[type].finditer(segment)]

def tokenize(source_code: str) -> list[Token]:
    tokens = [Token(text='{', type='module', location=Location('', 0, 0))]

    for line_num, line in enumerate(source_code.splitlines()):
        line = regexes['comment'].sub('', line).strip() # just remove all comments from each line

        if not line:
            continue

        matched_tokens = sorted(reduce(list.__add__, [find_token(k, line) for k in regexes.keys() if k != 'comment']), key=lambda token: token['start']) 

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
                            column=int(match['start'])
                        )
                    )
                )

    tokens.append(Token(text='}', type='module', location=Location('', tokens[-1].location.line+1, tokens[-1].location.column+1)))

    return tokens