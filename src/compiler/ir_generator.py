from typing import Dict
from compiler.types import Bool, Int, Type, Unit, SymbolTable
from compiler.ir import Call, CondJump, CopyPointer, IRVar, Instruction, LoadBoolConst, LoadIntConst, Label, Copy, Jump, LoadIntParam, LoadBoolParam, LoadPointerParam, ReturnValue
from compiler.ast import BreakContinue, Expression, FuncDef, Literal, Identifier, BinaryOp, IfThenElse, Block, Var, While, UnaryOp, Module, FuncCall

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
