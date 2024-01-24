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

    interpret
    TODO(student): add more

## IDE setup

Recommended VSCode extensions:

- Python
- Pylance
- autopep8
