import os
from compiler.assembler import assemble
from compiler.assembly_generator import generate_ns_assembly
from compiler.ast import Module
from compiler.ir import generate_root_var_types
from compiler.ir_generator import generate_ir
from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.type_checker import typecheck_module
from compiler.types import get_global_symbol_table_types
import unittest
import subprocess

def tokenize_parse_and_typecheck(inpt: str) -> Module:
    parsed = parse(tokenize(inpt))
    typecheck_module(parsed, get_global_symbol_table_types())
    return parsed

def run_test_case(test_count: int, test_namespace: str, test_case: tuple[str, str]) -> None:
    source, expected = test_case
    try:
        assembly = generate_ns_assembly(generate_ir(generate_root_var_types(), tokenize_parse_and_typecheck(source)))
        assemble(assembly, f'{test_namespace}_{test_count}_out')
        proc = subprocess.run([f'{os.getcwd()}/{test_namespace}_{test_count}_out'], capture_output = True, text = True)
        output = proc.stdout
        if output:
            assert output.strip() == expected
        else:
            raise Exception(f'End 2 End test failed on test case {test_namespace}_{test_count}')
    except Exception:
        raise Exception(f'Compiler failed at test {test_namespace}_{test_count}')

def read_test_cases() -> None:
    path = './tests/end2end/test_programs'
    files = [f for f in os.listdir(path)]

    for f in files:
        with open(f'{path}/{f}') as file:
            lines = file.readlines()
            i = 0
            count = 0
            while i < len(lines):
                inpt = lines[i].strip().split('#')[1]
                expected = lines[i+1].strip().split('#')[1]
                count += 1
                i = i + 3
                run_test_case(count, f, (inpt, expected))

class End2EndTest(unittest.TestCase):
    def test_all_cases(self) -> None:
        read_test_cases()