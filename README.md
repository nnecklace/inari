# Inari
Small programming language I made for fun. Also a town in finnish lapland.

## Setup

Requirements:

- [Pyenv](https://github.com/pyenv/pyenv) for installing Python 3.11+
    - Recommended installation method: the "automatic installer"
      i.e. `curl https://pyenv.run | bash`
- [Poetry](https://python-poetry.org/) for installing dependencies
    - Recommended installation method: the "official installer"
      i.e. `curl -sSL https://install.python-poetry.org | python3 -`

Install dependencies:

    # Install Python specified in `.python-version`
    pyenv install
    # Install dependencies specified in `pyproject.toml`
    poetry install

If `pyenv install` gives an error about `_tkinter`, you can ignore it.
If you see other errors, you may have to investigate.

If you have trouble with Poetry not picking up pyenv's python installation,
try `poetry env remove --all` and then `poetry install` again.

Typecheck and run tests:

    ./check.sh
    # or individually:
    poetry run mypy .
    poetry run pytest -vv

Run the compiler on a source code file:

    ./compiler.sh COMMAND path/to/source/code

where `COMMAND` may be one of these:

    `interpret` (runs the interpreter)
    `compile` (runs the compiler)
    `asm` (prints the assembly code produced by the program)
    `tc` (runs the typechecker)
    `ir` (prints ir code produced by the program)
    `flowgraph` (prints the flowgraph produced by the program)
    `dataflow` (prints the dataflow produced by the program)
    `parse` (runs the parser)


In some cases you might need to set `export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring`. Otherwise poetry does nothing and fails silently.

# Report

### Testing

Test coverage: 80% (dataflow framework no unit tests, otherwise test coverage would be > 95)
Unit tests: 201
End 2 end tests: 56

### Features Done

- [x] Tokenizer 
- [x] Parser
- [x] Interpreter
- [x] Typechecker
- [x] Ir generator
- [x] Assembly generator
- [x] Compiler
- [x] Base language

### Additional Features

- [x] Break Continue
- [x] Functions
- [x] Pointers
- [x] Dataflow (forward) framework (Chapter 8 tasks 1-4)

### Additional comments

#### Tokenizer

Multiline comments are not supported. 

The main level program is wrapped in `{}` tokens. This essentially means, that all top level programs are also blocks. These blocks are called __modules__. 

#### Interpreter

The interpreter only works on the base language, none of the additional features have been added there. Using any additional feature, such as break or continue, will result in interpreter crashing.

#### Break Continue

Break continue statements cannot return values. Breaks and continues can only occur in while loops.

#### Functions

No return statement exists. Function bodies are blocks, thus they work like blocks, where the last statement is the implicit return statement. 

```
fun f(): Int { 
    1+1 
}

print_int(f()) # prints out 2
```

Functions can call other functions, i.e. functions support mutual recursion.

```
fun f(x: Int): Int { 
    g(x)+x 
}

fun g(x: Int): Int { 
    x
}

var x: Int = f(10); # functions are like any other literal

print_int(x) # prints 20
```

Accessing globals from functions, while possible, result in undefined behaviour.

```
var x: Int = 10
fun f(): Int { 
    x
}

print_int(f()) # might print 10
```

Functions can have params passed to them

```
var x = 10; # var types optional
fun f(y: Int): Int { 
    y
}

print_int(f(x)) # prints 10
```

Shadowing top level vars works

```
var x = 10; 
fun f(x: Int): Int { 
    x + 1
} 

print_int(f(x)) # prints 11
```

Functions can have their own local vars

```
var x = 10; 
fun f(x: Int): Int {
    var y: Int = 10;
    x + y
} 

print_int(f(x)) # prints 20
```

Local vars don't leak

```
var x = 10; 
fun f(x: Int): Int {
    var y: Int = 10;
    x + y
} 

print_int(y) # <-- y not found
```

No known limit is known to function arguments. 17 arguments work at least as intended. However, weird stuff might happen with larger amounts of args. Stack space might end.
First 6 arguments are added to registers, the rest pushed to the stack.

```
fun f(a: Int, b: Int, c: Int, d: Int, e: Int, f: Int, g: Int, h: Int, i: Int, j: Int, k: Int, l: Int, m: Int, n: Int, o: Int, p: Int, q: Int): Int {
 p
}

print_int(f(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0)) # prints out 1
```

Functions cannot be assigned to variables 

```
fun f(x: Int): Int { 
    x 
} 

var y: Int = f; 

y(1) # will not work
```

#### Pointers

Unary operators `&` and `*` work. Although, `&` can only be followed by an identifier. `&1` will not work, neither will `&&x`. This is from some old context free grammar of C (no link to material), made sense to me so I made it like so.
Function pointers are not supported. Dangling pointers result in undefined behavior.

```
fun square(p: Int*): Unit {
    *p = *p * *p;
}

var x: Int = 3;
square(&x);
print_int(x);  # Prints 9
```

Pointers to pointers work as well

```
var x: Int = 10;
var y: Int* = &x;
var z: Int** = &y;

print_int(**z); # prints 10
```

#### Dataflow framework

Tasks 1-4 done in chapter 8. Time ran out so, tasks 5-6 remain undone. Dataflow framework and flowgraphs have only been tested manually. Unknown at this point if, and how many, bugs are present. 
There are many `./check.sh` errors with the dataflow namespace. There was limited time to clean that up.