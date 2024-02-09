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

    def test_tokenizer_bools(self) -> None:
        assert tokenize('if true then false') == [
            Token(location=LL, type='identifier', text='if'),
            Token(location=LL, type='bool_literal', text='true'),
            Token(location=LL, type='identifier', text='then'),
            Token(location=LL, type='bool_literal', text='false')
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

    def test_tokenizer_with_arithmetic_operations_without_spaces_and_only_identifiers(self) -> None:
        assert tokenize('a+b') == [
            Token(location=LL, type='identifier', text='a'),
            Token(location=LL, type='operator', text='+'),
            Token(location=LL, type='identifier', text='b')
        ]

    def test_tokenizer_function_call(self) -> None:
        assert tokenize('f(x, a + b)') == [
            Token(location=LL, type='identifier', text='f'),
            Token(location=LL, type='punctuation', text='('),
            Token(location=LL, type='identifier', text='x'),
            Token(location=LL, type='punctuation', text=','),
            Token(location=LL, type='identifier', text='a'),
            Token(location=LL, type='operator', text='+'),
            Token(location=LL, type='identifier', text='b'),
            Token(location=LL, type='punctuation', text=')')
        ]

    def test_tokenizer_with_arithmetic_operations_without_spaces_and_only_identifiers_and_punctuation(self) -> None:
        assert tokenize('{a+b;c-d,}') == [
            Token(location=LL, type='punctuation', text='{'),
            Token(location=LL, type='identifier', text='a'),
            Token(location=LL, type='operator', text='+'),
            Token(location=LL, type='identifier', text='b'),
            Token(location=LL, type='punctuation', text=';'),
            Token(location=LL, type='identifier', text='c'),
            Token(location=LL, type='operator', text='-'),
            Token(location=LL, type='identifier', text='d'),
            Token(location=LL, type='punctuation', text=','),
            Token(location=LL, type='punctuation', text='}')
        ]

    def test_tokenizer_complicated(self) -> None:
        assert tokenize('while a >= (2+5+(2+5))/(x/y)# we add a comment here') == [
            Token(location=LL, type='identifier', text='while'),
            Token(location=LL, type='identifier', text='a'),
            Token(location=LL, type='operator', text='>='),
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

    def test_tokenizer_recognizes_blocks(self):
        assert tokenize('{}') == [
            Token(location=LL, type='punctuation', text='{'),
            Token(location=LL, type='punctuation', text='}')
        ]

    def test_tokenizer_recognizes_blocks_with_semi_colon(self):
        assert tokenize('{};') == [
            Token(location=LL, type='punctuation', text='{'),
            Token(location=LL, type='punctuation', text='}'),
            Token(location=LL, type='punctuation', text=';')
        ]

    def test_tokenizer_multiple_punctuations(self):
        assert tokenize('{ b };;') == [
            Token(location=LL, type='punctuation', text='{'),
            Token(location=LL, type='identifier', text='b'),
            Token(location=LL, type='punctuation', text='}'),
            Token(location=LL, type='punctuation', text=';'),
            Token(location=LL, type='punctuation', text=';')
        ]
    
    def test_tokenizer_operators(self) -> None:
        assert tokenize('((-2)+3)-6*3%7/1<5>=100<=1000!=5') == [
            Token(location=LL, type='punctuation', text='('),
            Token(location=LL, type='punctuation', text='('),
            Token(location=LL, type='operator', text='-'),
            Token(location=LL, type='int_literal', text='2'),
            Token(location=LL, type='punctuation', text=')'),
            Token(location=LL, type='operator', text='+'),
            Token(location=LL, type='int_literal', text='3'),
            Token(location=LL, type='punctuation', text=')'),
            Token(location=LL, type='operator', text='-'),
            Token(location=LL, type='int_literal', text='6'),
            Token(location=LL, type='operator', text='*'),
            Token(location=LL, type='int_literal', text='3'),
            Token(location=LL, type='operator', text='%'),
            Token(location=LL, type='int_literal', text='7'),
            Token(location=LL, type='operator', text='/'),
            Token(location=LL, type='int_literal', text='1'),
            Token(location=LL, type='operator', text='<'),
            Token(location=LL, type='int_literal', text='5'),
            Token(location=LL, type='operator', text='>='),
            Token(location=LL, type='int_literal', text='100'),
            Token(location=LL, type='operator', text='<='),
            Token(location=LL, type='int_literal', text='1000'),
            Token(location=LL, type='operator', text='!='),
            Token(location=LL, type='int_literal', text='5')
        ]