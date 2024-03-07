from typing import Dict
from compiler.ir import Instruction, IRVar, Label, LoadIntConst, Jump, LoadBoolConst, Copy, CondJump, Call
from dataclasses import fields
from compiler.intrinsics import all_intrinsics, IntrinsicArgs
from compiler.types import get_global_symbol_table_types

class Locals:
    """Knows the memory location of every local variable."""
    _var_to_location: dict[IRVar, str]
    _stack_used: int

    def __init__(self, variables: list[IRVar]) -> None:
        start_loc = -8
        self._var_to_location = {}
        for var in variables:
            self._var_to_location[var] = str(start_loc)+'(%rbp)'
            start_loc += -8
        
        self._stack_used = -1*start_loc-8

    def get_ref(self, v: IRVar) -> str:
        """Returns an Assembly reference like `-24(%rbp)`
        for the memory location that stores the given variable"""
        return self._var_to_location[v]

    def stack_used(self) -> int:
        """Returns the number of bytes of stack space needed for the local variables."""
        return self._stack_used

def get_all_ir_variables(instructions: list[Instruction]) -> list[IRVar]:
    roots = get_global_symbol_table_types()
    result_list: list[IRVar] = []
    result_set: set[IRVar] = set()

    def add(v: IRVar) -> None:
        # we need to make sure we don't add globals to the stack
        if (v not in result_set) and (v.name not in roots.bindings.keys()):
            result_list.append(v)
            result_set.add(v)

    for insn in instructions:
        for field in fields(insn):
            value = getattr(insn, field.name)
            if isinstance(value, IRVar):
                add(value)
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, IRVar):
                        add(v)
    return result_list 

def generate_ns_assembly(ns_ins: Dict[str, list[Instruction]]) -> str:
    assembly = []
    for ins in ns_ins.values:
        assembly.append(generate_assembly(ins))

    return ''.join(ass+'\n' for ass in assembly)

def generate_assembly(instructions: list[Instruction]) -> str:
    lines = []
    def emit(line: str) -> None: lines.append(line)

    vars = get_all_ir_variables(instructions)

    locals = Locals(
        variables=vars
    )

    emit('.extern print_int')
    emit('.extern print_bool')
    emit('.extern read_int')
    emit('.global main')
    emit('.type main, @function')
    emit('')
    emit('.section .text')
    emit('')
    emit('main:')
    emit(f'pushq %rbp')
    emit(f'movq %rsp, %rbp')
    emit(f'subq ${locals._stack_used}, %rsp')
    emit('')
    emit('.Lstart:')

    for insn in instructions:
        emit('# ' + str(insn))
        match insn:
            case Label():
                emit("")
                # ".L" prefix marks the symbol as "private".
                # This makes GDB backtraces look nicer too:
                # https://stackoverflow.com/a/26065570/965979
                emit(f'.L{insn.name}:')
            case LoadBoolConst():
                v = 0
                if insn.value == True:
                    v += 1                    

                emit(f'movq ${v}, {locals.get_ref(insn.dest)}')
            case Copy():
                emit(f'movq {locals.get_ref(insn.source)}, %rax')
                emit(f'movq %rax, {locals.get_ref(insn.dest)}')
            case LoadIntConst():
                if -2**31 <= insn.value < 2**31:
                    emit(f'movq ${insn.value}, {locals.get_ref(insn.dest)}')
                else:
                    # Due to a quirk of x86-64, we must use
                    # a different instruction for large integers.
                    # It can only write to a register,
                    # not a memory location, so we use %rax
                    # as a temporary.
                    emit(f'movabsq ${insn.value}, %rax')
                    emit(f'movq %rax, {locals.get_ref(insn.dest)}')
            case Jump():
                emit(f'jmp .L{insn.label.name}')
            case CondJump():
                emit(f'cmpq $0, {locals.get_ref(insn.cond)}')
                emit(f'jne .L{insn.then_label.name}')
                emit(f'jmp .L{insn.else_label.name}')
            case Call():
                if insn.fun.name in all_intrinsics:
                    all_intrinsics[insn.fun.name](IntrinsicArgs(
                        arg_refs=[locals.get_ref(arg) for arg in insn.args],
                        result_register='%rax',
                        emit=emit
                    ))

                if insn.fun.name == 'print_int' or insn.fun.name == 'print_bool':
                    emit(f'movq {locals.get_ref(insn.args[0])}, %rdi')
                    emit(f'callq {insn.fun.name}')

                emit(f'movq %rax, {locals.get_ref(insn.dest)}')

    emit(f'movq $0, %rax')
    emit(f'movq %rbp, %rsp')
    emit(f'popq %rbp')
    emit(f'ret')

    return ''.join(line+'\n' for line in lines)