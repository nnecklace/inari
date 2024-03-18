from typing import Dict, Self, Set
from compiler.ir import Call, CondJump, IRVar, Instruction, LoadBoolConst, LoadIntConst, Label, Copy, Jump, LoadIntParam, LoadBoolParam, LoadPointerParam


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