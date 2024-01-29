from compiler.tokenizer import tokenize
from compiler.token import Token
from compiler.location import L

import unittest

LL = L('', 0, 0)

class TokenizerTest(unittest.TestCase):
    def test_tokenizer_comment_forward_slash(self) -> None:
        assert tokenize('// this is a basic comment') == []

    def test_tokenizer_comment_forward_slas_with_new_line(self) -> None:
        assert tokenize('// this is a basic comment\n1') == [Token(location=LL, type='int_literal', text='1')]

    def test_tokenizer_comment_hash_with_new_line(self) -> None:
        assert tokenize('#this is a basic comment\n2') == [Token(location=LL, type='int_literal', text='2')]

    def test_tokenizer_comments_within_comments(self) -> None:
        assert tokenize('// this is a # comment with a comment\nif') == [Token(location=LL, type='identifier', text='if')]

    def test_tokenizer_comments_within_comments_and_comments_on_newlines(self) -> None:
        assert tokenize('// this is a # comment with a comment\nif\n# hello world') == [Token(location=LL, type='identifier', text='if')]

    def test_tokenizer_basics(self) -> None:
        assert tokenize('if  3\nwhile') == [
            Token(location=LL, type='identifier', text='if'),
            Token(location=LL, type='int_literal', text='3'),
            Token(location=LL, type='identifier', text='while')
        ]

    def test_tokenizer_raise_error(self) -> None:
        self.assertRaises(ValueError, tokenize, '2+3*5?')

    def test_tokenizer_with_arithmetic_operations(self) -> None:
        assert tokenize('if 3 <= 5 + 4') == [
            Token(location=LL, type='identifier', text='if'),
            Token(location=LL, type='int_literal', text='3'),
            Token(location=LL, type='operator', text='<='),
            Token(location=LL, type='int_literal', text='5'),
            Token(location=LL, type='operator', text='+'),
            Token(location=LL, type='int_literal', text='4')
        ]

    def test_tokenizer_with_arithmetic_operations_without_spaces(self) -> None:
        assert tokenize('if 3<= 5+4') == [
            Token(location=LL, type='identifier', text='if'),
            Token(location=LL, type='int_literal', text='3'),
            Token(location=LL, type='operator', text='<='),
            Token(location=LL, type='int_literal', text='5'),
            Token(location=LL, type='operator', text='+'),
            Token(location=LL, type='int_literal', text='4')
        ]
    
    def test_tokenizer_with_arithmetic_operations_without_spaces_2(self) -> None:
        assert tokenize('1+2') == [
            Token(location=LL, type='int_literal', text='1'),
            Token(location=LL, type='operator', text='+'),
            Token(location=LL, type='int_literal', text='2')
        ]

    def test_tokenizer_complicated(self) -> None:
        assert tokenize('while a => (2+5+(2+5))/(x/y)# we add a comment here') == [
            Token(location=LL, type='identifier', text='while'),
            Token(location=LL, type='identifier', text='a'),
            Token(location=LL, type='operator', text='=>'),
            Token(location=LL, type='punctuation', text='('),
            Token(location=LL, type='int_literal', text='2'),
            Token(location=LL, type='operator', text='+'),
            Token(location=LL, type='int_literal', text='5'),
            Token(location=LL, type='operator', text='+'),
            Token(location=LL, type='punctuation', text='('),
            Token(location=LL, type='int_literal', text='2'),
            Token(location=LL, type='operator', text='+'),
            Token(location=LL, type='int_literal', text='5'),
            Token(location=LL, type='punctuation', text=')'),
            Token(location=LL, type='punctuation', text=')'),
            Token(location=LL, type='operator', text='/'),
            Token(location=LL, type='punctuation', text='('),
            Token(location=LL, type='identifier', text='x'),
            Token(location=LL, type='operator', text='/'),
            Token(location=LL, type='identifier', text='y'),
            Token(location=LL, type='punctuation', text=')')
        ]