from typing import Dict, Self, Set
from compiler.types import Bool, Int, Type, Unit, SymbolTable
from compiler.ir import Call, CondJump, CopyPointer, IRVar, Instruction, LoadBoolConst, LoadIntConst, Label, Copy, Jump, LoadIntParam, LoadBoolParam, LoadPointerParam, ReturnValue
from compiler.ast import BreakContinue, Expression, FuncDef, Literal, Identifier, BinaryOp, IfThenElse, Block, Var, While, UnaryOp, Module, FuncCall

def generate_blocks(ins: Dict[str, list[Instruction]]) -> Dict[str, list[list[tuple[IRVar, int]]]]:
    block_dict: Dict[str, list[list[tuple[IRVar, int]]]] = {}

    unique_indx = 0

    for name, instructions in ins.items():
        block_dict[name] = []
        block: list[tuple[Instruction, int]] = []
        for instruction in instructions:
            if isinstance(instruction, Label) and len(block) > 0:
                block_dict[name].append(block)
                block = []
            block.append((instruction, unique_indx))
            unique_indx += 1
            if isinstance(instruction, CondJump) or isinstance(instruction, Jump):
                block_dict[name].append(block)
                block = []

        if block:
            block_dict[name].append(block)

    return block_dict

def generate_flow_graph(ns_blocks: Dict[str, list[list[tuple[IRVar, int]]]]) -> Dict[str, Dict[str, list[Instruction | str]]]:
    graph = {}

    for name, blocks in ns_blocks.items():
        for i, block in enumerate(blocks):
            graph[block[0][0].name] = {'block': block,
                                    'edges': []}

            if isinstance(block[0][-1], Jump):
                graph[block[0][0].name]['edges'].append(block[0][-1].label.name)
            elif isinstance(block[0][-1], CondJump):
                graph[block[0][0].name]['edges'].append(block[0][-1].then_label.name)
                graph[block[0][0].name]['edges'].append(block[0][-1].else_label.name)
            else:
                if i+1 < len(blocks):
                    graph[block[0][0].name]['edges'].append(blocks[i+1][0][0].name)

    return graph

type State = Dict[str, Set[int]]

class DataFlow:
    ins: Dict[str, list[list[tuple[Instruction, int]]]] = {}
    inp: Dict[int, State] = {}
    outp: Dict[int, State] = {}
    change_log_in: Dict[int, bool] = {}
    change_log_out: Dict[int, bool] = {}

    def set_initial_state(self: Self):
        init_state = {}
        ins_count = 0
        for name, blocks in self.ins.items():
            for block in blocks:
                for var, _ in block:
                    ins_count += 1
                    self.change_log_in[_] = False
                    self.change_log_out[_] = False
                    match var:
                        case LoadBoolConst():
                            init_state[var.dest.name] = set([-2])
                        case LoadIntConst():
                            init_state[var.dest.name] = set([-2])
                        case Copy():
                            init_state[var.source.name] = set([-2])
                            init_state[var.dest.name] = set([-2])
                        case Call():
                            init_state[var.fun.name] = set([-1])
                            for arg in var.args:
                                init_state[arg.name] = set([-2])
                            init_state[var.dest.name] = set([-2])
                        case CondJump():
                            init_state[var.cond.name] = set([-2])
                        case LoadIntParam():
                            init_state[var.symbol.name] = set([-2])
                            init_state[var.dest.name] = set([-2])
                        case LoadBoolParam():
                            init_state[var.symbol.name] = set([-2])
                            init_state[var.dest.name] = set([-2])

        for i in range(0, ins_count+1):
            self.inp[i] = {}
            self.outp[i] = {}
            for var in init_state.keys():
                self.inp[i][var] = set([])
                self.outp[i][var] = set([])

        self.inp[0] = init_state

    def __init__(self: Self, ins: Dict[str, list[list[tuple[Instruction, int]]]]) -> None:
        self.ins = ins

    def init_change_log(self: Self, value: bool) -> None:
        for key in self.change_log_in.keys():
            self.change_log_in[key] = value
            self.change_log_out[key] = value

    def compute(self: Self) -> None:
        self.set_initial_state()
        first_round = True

        self.init_change_log(True)

        while any(self.change_log_out.values()) or any(self.change_log_in.values()):
            if not first_round:
                self.init_change_log(False)
            for name, blocks in self.ins.items():
                for block in blocks:
                    for ins, index in block:
                        if isinstance(ins, Label):
                            prev = self.inp[index].copy()
                            jumps = self.jumps_to(ins)
                            if any([self.change_log_out[j] for j in jumps]):
                                self.inp[index] = self.merge(jumps)
                            if not self.equal(prev, self.inp[index]):
                                self.change_log_in[index] = True

                        if self.change_log_in[index]:
                            prev = self.outp[index].copy()
                            self.transfer(index, ins)
                            if not self.equal(prev, self.outp[index]):
                                self.change_log_out[index] = True
                            if index+1 < len(block):
                                prev = self.inp[index+1].copy()
                                self.inp[index+1] = self.outp[index].copy()
                                if not self.equal(prev, self.inp[index+1]):
                                    self.change_log_in[index+1] = True
            first_round = False

    def print_out_flows(self: Self) -> None:
        for steps, state in self.outp.items():
            if len([s for s in state.values() if len(s) > 0]) == 0:
                continue
            print(f'Step {steps}')
            for var, sets in state.items():
                if len(sets) == 0:
                    continue
                print(f'{var} => {sets}')
            print()

    def print_in_flows(self: Self) -> None:
        for steps, state in self.inp.items():
            if len([s for s in state.values() if len(s) > 0]) == 0:
                continue
            print(f'Step {steps}')
            for var, sets in state.items():
                if len(sets) == 0:
                    continue
                print(f'{var} => {sets}')
            print()

    def equal(self: Self, state_a: State, state_b: State) -> bool:
        for key, value in state_a.items():
            if value != state_b[key]:
                return False

        return set(state_a.keys()) == set(state_b.keys())

    def jumps_to(self: Self, label: Label) -> list[int]:
        jumps = []
        for name, blocks in self.ins.items():
            for block in blocks:
                for var, j in block:
                    match var:
                        case CondJump():
                            if var.then_label.name == label.name or var.else_label == label.name:
                                jumps.append(j)
                        case Jump():
                            if var.label.name == label.name:
                                jumps.append(j)

        return jumps

    def merge(self: Self, jumps: list[int]) -> State:
        merger = self.outp[jumps[0]]
        for j in jumps[1:]:
            for key, value in self.outp[j].items():
                merger[key].union(value)

        return merger

    def transfer(self: Self, index: int, instruction: Instruction) -> None:
        match instruction:
            case LoadBoolConst() | LoadIntConst() | Copy()| Call() | LoadIntParam() | LoadBoolParam() | LoadPointerParam():
                dest = instruction.dest.name
                curr_in = self.inp[index].copy()
                for key in curr_in.keys():
                    if key == dest:
                        self.outp[index][dest] = set([index])


def generate_ir(
    # 'root_types' parameter should map all global names
    # like 'print_int' and '+' to their types.
    root_types: dict[IRVar, Type], # type: ignore[valid-type]
    root_module: Module 
) -> Dict[str, list[Instruction]]:
    var_types: dict[IRVar, Type] = root_types.copy() # type: ignore[valid-type]
    # 'var_unit' is used when an expression's type is 'Unit'.
    var_unit = IRVar('unit')
    var_types[var_unit] = Unit
    var_counts = {'x': 0, 'if': 0, 'while': 0, 'and': 0, 'or': 0}

    def new_var(t: Type) -> IRVar: # type: ignore[valid-type]
        # Create a new unique IR variable and
        # add it to var_types
        num = var_counts['x']+1
        var_x = IRVar('x'+str(num))
        var_counts['x'] = num
        var_types[var_x] = t
        return var_x

    # We collect the IR instructions that we generate
    # into this list.
    ins: list[Instruction] = []
    loop_context: list[tuple[Label, Label]] = []
    ns_ins: Dict[str, list[Instruction]] = {'main': []}

    functions: list[FuncDef] = []

    # This function visits an AST node,
    # appends IR instructions to 'ins',
    # and returns the IR variable where
    # the emitted IR instructions put the result.
    #
    # It uses a symbol table to map local variables
    # (which may be shadowed) to unique IR variables.
    # The symbol table will be updated in the same way as
    # in the interpreter and type checker.
    def visit(symbol_table: SymbolTable[IRVar], expr: Expression) -> IRVar:
        loc = expr.location

        match expr:
            case Literal():
                # Create an IR variable to hold the value,
                # and emit the correct instruction to
                # load the constant value.
                match expr.value:
                    case bool():
                        var = new_var(Bool)
                        ins.append(LoadBoolConst(loc, expr.value, var))
                    case int():
                        var = new_var(Int)
                        ins.append(LoadIntConst(loc, expr.value, var))
                    case None:
                        var = var_unit
                    case _:
                        raise Exception(f"{loc}: unsupported literal: {type(expr.value)}")

                # Return the variable that holds
                # the loaded value.
                return var

            case BreakContinue():
                if len(loop_context) == 0:
                    raise Exception(f'Illegal use of {expr.name} can only be used within a while loop')

                while_start, while_end = loop_context[-1]

                if expr.name == 'break':
                    ins.append(Jump(loc, while_end))
                elif expr.name == 'continue':
                    ins.append(Jump(loc, while_start))

                return var_unit

            case FuncDef():
                functions.append(expr)
                symbol_table.add_local(expr.name.name, IRVar(expr.name.name))
                return var_unit

            case FuncCall():
                args = [visit(symbol_table, arg) for arg in expr.args]
                var_result = new_var(expr.type)
                ins.append(Call(loc, symbol_table.require(expr.name.name), args, var_result))
                return var_result

            case Identifier():
                # Look up the IR variable that corresponds to
                # the source code variable.
                return symbol_table.require(expr.name)
            
            case UnaryOp():
                var_body = visit(symbol_table, expr.right)
                var_result = new_var(expr.type)
                var_op = symbol_table.require(f'unary_{expr.op}')
                ins.append(Call(loc, var_op, [var_body], var_result))
                return var_result
            
            case BinaryOp():
                if expr.op == '=':
                    if not isinstance(expr.left, Identifier) and (isinstance(expr.left, UnaryOp) and expr.left.op != '*'):
                        # this check should ideally be moved to the typechecker
                        raise Exception(f'Expected left hand side of assignment in {expr.location} to be an identifier')
                    var_right = visit(symbol_table, expr.right)
                    if isinstance(expr.left, UnaryOp):
                        var_left = visit(symbol_table, expr.left.right)
                        ins.append(CopyPointer(loc, var_right, var_left))
                    else:
                        var_left = symbol_table.require(expr.left.name) # type: ignore[attr-defined]
                        ins.append(Copy(loc, var_right, var_left))
                    return var_unit
                
                if expr.op == 'and' or expr.op == 'or':
                    var_count = var_counts[expr.op]+1
                    l_right = Label(loc,expr.op+'_right'+str(var_count))
                    l_skip = Label(loc,expr.op+'_skip'+str(var_count))
                    l_end = Label(loc,expr.op+'_end'+str(var_count))
                    var_counts[expr.op] = var_count
                    var_left = visit(symbol_table, expr.left)

                    if expr.op == 'and':
                        ins.append(CondJump(loc, var_left, l_right, l_skip))
                    else:
                        ins.append(CondJump(loc, var_left, l_skip, l_right))

                    ins.append(l_right)
                    var_right = visit(symbol_table, expr.right)
                    var_result = new_var(Bool)
                    ins.append(Copy(loc, var_right, var_result))
                    ins.append(Jump(loc, l_end))
                    ins.append(l_skip)
                    ins.append(LoadBoolConst(loc, (expr.op == 'or'), var_result))
                    ins.append(Jump(loc, l_end))
                    ins.append(l_end)

                    return var_result

                if expr.op == '==' or expr.op == '!=':
                    var_op = IRVar(expr.op)
                else:
                    var_op = symbol_table.require(expr.op)

                var_left = visit(symbol_table, expr.left)
                var_right = visit(symbol_table, expr.right)
                var_result = new_var(expr.type)

                ins.append(Call(loc, var_op, [var_left, var_right], var_result))
                return var_result

            case IfThenElse():
                if expr.otherwise is None:
                    if_count = var_counts['if']+1
                    l_then = Label(loc,'then'+str(if_count))
                    l_end = Label(loc,'if_end'+str(if_count))
                    var_counts['if'] = if_count
                    var_cond = visit(symbol_table, expr.cond)
                    ins.append(CondJump(loc, var_cond, l_then, l_end))
                    ins.append(l_then)
                    visit(symbol_table, expr.then)
                    ins.append(l_end)

                    return var_unit
                else:
                    if_count = var_counts['if']+1
                    l_then = Label(loc,'then'+str(if_count))
                    l_else = Label(loc,'else'+str(if_count))
                    l_end = Label(loc,'if_end'+str(if_count)) 
                    var_counts['if'] = if_count
                    var_cond = visit(symbol_table, expr.cond)
                    ins.append(CondJump(loc, var_cond, l_then, l_else))
                    ins.append(l_then)
                    var_result = new_var(expr.then.type)
                    var_then = visit(symbol_table, expr.then)
                    ins.append(Copy(loc, var_then, var_result))
                    ins.append(Jump(loc, l_end))
                    ins.append(l_else)
                    var_else = visit(symbol_table, expr.otherwise)
                    ins.append(Copy(loc, var_else, var_result))
                    ins.append(l_end)

                    return var_result

            case While():
                while_count = var_counts['while']+1
                l_while_start = Label(loc, 'while_start'+str(while_count))
                l_while_body = Label(loc, 'while_body'+str(while_count))
                l_while_end = Label(loc, 'while_end'+str(while_count))
                var_counts['while'] = while_count
                ins.append(l_while_start)
                var_cond = visit(symbol_table, expr.cond)
                ins.append(CondJump(loc, var_cond, l_while_body, l_while_end))
                ins.append(l_while_body)
                loop_context.append((l_while_start, l_while_end))
                var_result = visit(symbol_table, expr.body)
                loop_context.pop()
                ins.append(Jump(loc, l_while_start))
                ins.append(l_while_end)

                return var_unit

            case Var():
                var_init = visit(symbol_table, expr.initialization)
                var_result = new_var(expr.type)
                ins.append(Copy(loc, var_init, var_result))
                symbol_table.add_local(expr.name.name, var_result)
                return var_result

            case Block():
                new_symbol_table = SymbolTable[IRVar](bindings={}, parent=symbol_table)
                for exp in expr.statements[:len(expr.statements)-1]:
                    visit(new_symbol_table, exp)
                
                return visit(new_symbol_table, expr.statements[-1])
            
        raise Exception('Unknown expression type')

    # Convert 'root_types' into a SymTab
    # that maps all available global names to
    # IR variables of the same name.
    # In the Assembly generator stage, we will give
    # definitions for these globals. For now,
    # they just need to exist.
    root_symtab = SymbolTable[IRVar](bindings={}, parent=None)
    for v in root_types.keys():
        root_symtab.add_local(v.name, v)

    # Start visiting the AST from the root.
    ins.append(Label(root_module.location, 'Start_1'))
    for exp in root_module.expressions[:len(root_module.expressions)-1]:
        visit(root_symtab, exp)

    var_final_result = visit(root_symtab, root_module.expressions[-1])

    if var_types[var_final_result] == Int:
        # Emit a call to 'print_int'
        x_count = var_counts['x']+1
        ins.append(Call(root_module.location, root_symtab.require('print_int'), [var_final_result], IRVar('x'+str(x_count)))) 
        var_counts['x'] = x_count
    elif var_types[var_final_result] == Bool:
        # Emit a call to 'print_bool'
        x_count = var_counts['x']+1
        ins.append(Call(root_module.location, root_symtab.require('print_bool'), [var_final_result], IRVar('x'+str(x_count))))
        var_counts['x'] = x_count

    ins.append(ReturnValue(root_module.location, IRVar('-1')))
    ns_ins['main'] = ins
    for f in functions:
        ins = []
        ins.append(Label(f.location, f'Start_{f.name.name}'))
        new_symbol_table = SymbolTable[IRVar](bindings={}, parent=root_symtab)
        for arg in f.args:
            param = new_var(arg.declared_type)
            if arg.declared_type is Int:
                ins.append(LoadIntParam(arg.location, IRVar(arg.name), param))
            elif arg.declared_type is Bool:
                ins.append(LoadBoolParam(arg.location, IRVar(arg.name), param))
            else:
                # argument has to be pointer
                ins.append(LoadPointerParam(arg.location, IRVar(arg.name), param))
            new_symbol_table.add_local(arg.name, param)
        return_value = visit(new_symbol_table, f.body)
        ins.append(ReturnValue(f.location, return_value))
        ns_ins[f.name.name] = ins

    return ns_ins
