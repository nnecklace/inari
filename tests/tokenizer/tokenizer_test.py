from compiler.tokenizer import tokenize
from compiler.token import Token
from compiler.location import L

LL = L('', 0, 0)

def test_tokenizer_comment_forward_slash() -> None:
    assert tokenize('// this is a basic comment') == []

def test_tokenizer_comment_forward_slas_with_new_line() -> None:
    assert tokenize('// this is a basic comment\n1') == [Token(location=LL, type='int_literal', text='1')]

def test_tokenizer_comment_hash_with_new_line() -> None:
    assert tokenize('#this is a basic comment\n2') == [Token(location=LL, type='int_literal', text='2')]

def test_tokenizer_comments_within_comments() -> None:
    assert tokenize('// this is a # comment with a comment\nif') == [Token(location=LL, type='identifier', text='if')]

def test_tokenizer_comments_within_comments_and_comments_on_newlines() -> None:
    assert tokenize('// this is a # comment with a comment\nif\n# hello world') == [Token(location=LL, type='identifier', text='if')]

def test_tokenizer_basics() -> None:
    assert tokenize('if  3\nwhile') == [
        Token(location=LL, type='identifier', text='if'),
        Token(location=LL, type='int_literal', text='3'),
        Token(location=LL, type='identifier', text='while')
    ]

def test_tokenizer_raise_error() -> None:
    assert tokenize('2+3*5?') == [ # find a way to test exceptions
        Token(location=LL, type='identifier', text='if'),
    ]

def test_tokenizer_with_arithmetic_operations() -> None:
    assert tokenize('if 3 <= 5 + 4') == [
        Token(location=LL, type='identifier', text='if'),
        Token(location=LL, type='int_literal', text='3'),
        Token(location=LL, type='operator', text='<='),   
        Token(location=LL, type='int_literal', text='5'),
        Token(location=LL, type='operator', text='+'),
        Token(location=LL, type='int_literal', text='4')
    ]

def test_tokenizer_with_arithmetic_operations_without_spaces() -> None:
    assert tokenize('if 3<= 5+4') == [
        Token(location=LL, type='identifier', text='if'),
        Token(location=LL, type='int_literal', text='3'),
        Token(location=LL, type='operator', text='<='),   
        Token(location=LL, type='int_literal', text='5'),
        Token(location=LL, type='operator', text='+'),
        Token(location=LL, type='int_literal', text='4')
    ]