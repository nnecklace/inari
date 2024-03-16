import sys
from compiler.assembler import assemble
from compiler.ast import Expression
from compiler.ir import generate_root_var_types
from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.ir_generator import generate_blocks, generate_flow_graph, generate_ir
from compiler.type_checker import typecheck_module
from compiler.types import get_global_symbol_table_types
from compiler.assembly_generator import generate_assembly, generate_ns_assembly

# TODO(student): add more commands as needed
usage = f"""
Usage: {sys.argv[0]} <command> [source_code_file]

Command 'interpret':
    Runs the interpreter on source code.

Common arguments:
    source_code_file        Optional. Defaults to standard input if missing.
 """.strip() + "\n"

def tokenize_parse_and_typecheck(inpt: str) -> Expression:
    parsed = parse(tokenize(inpt))
    typecheck_module(parsed, get_global_symbol_table_types())
    return parsed

def main() -> int:
    command: str | None = None
    input_file: str | None = None
    for arg in sys.argv[1:]:
        if arg in ['-h', '--help']:
            print(usage)
            return 0
        elif arg.startswith('-'):
            raise Exception(f"Unknown argument: {arg}")
        elif command is None:
            command = arg
        elif input_file is None:
            input_file = arg
        else:
            raise Exception("Multiple input files not supported")

    def read_source_code() -> str:
        if input_file is not None:
            with open(input_file) as f:
                return f.read()
        else:
            return sys.stdin.read()

    if command is None:
        print(f"Error: command argument missing\n\n{usage}", file=sys.stderr)
        return 1

    if command == 'interpret':
        source_code = read_source_code()
        ...  # TODO(student)
    elif command == 'compile':
        source = tokenize_parse_and_typecheck(read_source_code())
        ins = generate_ir(generate_root_var_types(),source)
        asm = generate_ns_assembly(ins)
        assemble(asm, 'out')
    elif command == 'ir':
        source = tokenize_parse_and_typecheck(read_source_code())
        ins = generate_ir(generate_root_var_types(),source)
        for k, v in ins.items():
            print(f'{k}:')
            for i in v:
                print(i)
            print()

        print()
        blocks = generate_blocks(ins)
        for k, bs in blocks.items():
            for b in bs:
                print('Printing block')
                print(''.join(i[0].__str__()+'\n' for i in b))

        graph = generate_flow_graph(blocks)

        for l, g in graph.items():
            print('------------')
            print('Node label: ' + l + '\n')
            print('Block: \n' + ''.join(i[0].__str__()+'\n' for i in g['block']))
            print('Edges: \n' + ''.join(j+' ' for j in g['edges']))
            print()

    elif command == 'asm':
        source = tokenize_parse_and_typecheck(read_source_code())
        ins = generate_ir(generate_root_var_types(),source)
        asm = generate_ns_assembly(ins)
        print(asm)
    elif command == 'tc':
        print(tokenize_parse_and_typecheck(read_source_code()))
    else:
        print(f"Error: unknown command: {command}\n\n{usage}", file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
