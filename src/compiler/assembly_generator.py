from typing import Dict
from compiler.ir import CopyPointer, Instruction, IRVar, Label, LoadBoolParam, LoadIntConst, Jump, LoadBoolConst, Copy, CondJump, Call, LoadIntParam, LoadPointerParam, ReturnValue
from dataclasses import fields
from compiler.intrinsics import all_intrinsics, IntrinsicArgs
from compiler.types import get_global_symbol_table_types

class Locals:
    """Knows the memory location of every local variable."""
    _var_to_location: dict[str, str]
    _stack_used: int

    def __init__(self, variables: list[IRVar]) -> None:
        start_loc = -8
        self._var_to_location = {}
        for var in variables:
            self._var_to_location[var.name] = str(start_loc)+'(%rbp)'
            start_loc += -8
        
        self._stack_used = -1*start_loc-8

    def get_ref(self, v: IRVar) -> str:
        """Returns an Assembly reference like `-24(%rbp)`
        for the memory location that stores the given variable"""
        return self._var_to_location[v.name]

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

def emit_global(ns: list[str]) -> str:
    lines = []
    lines.append('.extern print_int')
    lines.append('.extern print_bool')
    lines.append('.extern read_int')
    for n in ns:
        lines.append(f'.global {n}')
    for n in ns:
        lines.append(f'.type {n}, @function')
    lines.append('')
    lines.append('.section .text')
    lines.append('')

    return ''.join(line+'\n' for line in lines)

def generate_ns_assembly(ns_ins: Dict[str, list[Instruction]]) -> str:
    assembly = []
    for k, v in ns_ins.items():
        assembly.append(generate_assembly(k,v))

    # python doesn't understand what dict_keys is, so I just ignore this
    return emit_global(ns_ins.keys())+''.join(ass+'\n' for ass in assembly) # type: ignore[arg-type]

def generate_assembly(ns:str, instructions: list[Instruction]) -> str:
    lines = []
    param_registers = ['%rdi', '%rsi', '%rdx', '%rcx', '%r8', '%r9']
    param_count = 0
    stack_arg_address = 16
    def emit(line: str) -> None: lines.append(line)

    vars = get_all_ir_variables(instructions)

    locals = Locals(
        variables=vars
    )

    emit(f'{ns}:')
    emit(f'pushq %rbp')
    emit(f'movq %rsp, %rbp')
    emit(f'subq ${locals._stack_used}, %rsp')
    emit('')
    emit(f'.L{ns}_start:')
    emit('')

    for insn in instructions:
        emit('# ' + str(insn))
        match insn:
            case Label():
                emit("")
                # ".L" prefix marks the symbol as "private".
                # This makes GDB backtraces look nicer too:
                # https://stackoverflow.com/a/26065570/965979
                emit(f'.L{ns}_{insn.name}:')
            case LoadBoolConst():
                v = 0
                if insn.value == True:
                    v += 1                    

                emit(f'movq ${v}, {locals.get_ref(insn.dest)}')
            case Copy():
                emit(f'movq {locals.get_ref(insn.source)}, %rax')
                emit(f'movq %rax, {locals.get_ref(insn.dest)}')
            case CopyPointer():
                emit(f'movq {locals.get_ref(insn.source)}, %rax')
                emit(f'movq {locals.get_ref(insn.dest)}, %rbx')
                emit(f'movq %rax, (%rbx)')
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
            case LoadIntParam() | LoadBoolParam() | LoadPointerParam():
                if param_count < len(param_registers):
                    emit(f'movq {param_registers[param_count]}, {locals.get_ref(insn.dest)}')
                else:
                    emit(f'movq {stack_arg_address}(%rbp), {locals.get_ref(insn.dest)}')
                    stack_arg_address += 8
                param_count += 1
            case Jump():
                emit(f'jmp .L{ns}_{insn.label.name}')
            case CondJump():
                emit(f'cmpq $0, {locals.get_ref(insn.cond)}')
                emit(f'jne .L{ns}_{insn.then_label.name}')
                emit(f'jmp .L{ns}_{insn.else_label.name}')
            case Call():
                if insn.fun.name in all_intrinsics:
                    all_intrinsics[insn.fun.name](IntrinsicArgs(
                        arg_refs=[locals.get_ref(arg) for arg in insn.args],
                        result_register='%rax',
                        emit=emit
                    ))
                elif insn.fun.name == 'print_int' or insn.fun.name == 'print_bool':
                    emit(f'movq {locals.get_ref(insn.args[0])}, %rdi')
                    emit(f'callq {insn.fun.name}')
                elif insn.fun.name == 'read_int':
                    emit(f'callq {insn.fun.name}')
                else:
                    remaining_params = []
                    if len(insn.args) > len(param_registers):
                        remaining_params = insn.args[len(param_registers):]

                    for indx, arg in enumerate(insn.args[:len(param_registers)]):
                        emit(f'movq {locals.get_ref(arg)}, {param_registers[indx]}')

                    if remaining_params:
                        for param in remaining_params:
                            emit(f'pushq {locals.get_ref(param)}')

                    emit(f'call {insn.fun.name}')
                    emit(f'addq ${8*len(remaining_params)}, %rsp')

                emit(f'movq %rax, {locals.get_ref(insn.dest)}')
            case ReturnValue():
                if ns == 'main':
                    emit(f'movq $0, %rax')
                else:
                    emit(f'movq {locals.get_ref(insn.var)}, %rax')

    emit('')
    emit(f'.L{ns}_end:')
    emit('')

    emit(f'movq %rbp, %rsp')
    emit(f'popq %rbp')
    emit(f'ret')

    return ''.join(line+'\n' for line in lines)