from compiler.tokenizer import tokenize 

def test_tokenizer_comment_forward_slash():
    assert tokenize('// this is a basic comment') == []

def test_tokenizer_comment_forward_slas_with_new_line():
    assert tokenize('// this is a basic comment\n1') == ['1']

def test_tokenizer_comment_hash_with_new_line():
    assert tokenize('#this is a basic comment\n2') == ['2']

def test_tokenizer_basics():
    assert tokenize('if  3\nwhile') == ['if', '3', 'while']