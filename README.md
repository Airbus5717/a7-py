# A7 Programming Language Compiler

This is a Python implementation of a compiler for the A7 programming language.
A7 is a statically-typed, procedural language with C-style syntax, manual 
memory management, and compile-time generics.

## Setup

### Prerequisites

- **Python 3.13+**: Required for running the compiler
- **uv**: Modern Python package manager (recommended for dependency management)

### Installing uv

If you don't have uv installed, install it using one of these methods:

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative (pip):**
```bash
pip install uv
```

### Clone and Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd a7-py
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

This will create a virtual environment and install all required dependencies including pytest and rich.

## Usage

### Running the Compiler

**Using uv (recommended):**
```bash
uv run python main.py <file.a7>
```

**Using the shell script:**
```bash
./run.sh <file.a7>
```

**Direct Python (if dependencies are installed):**
```bash
python main.py <file.a7>
```

### Example

Try compiling one of the example programs:
```bash
uv run python main.py examples/001_hello.a7
```

## Testing

```bash
uv run pytest
```

The compiler currently implements a complete lexer/tokenizer and recursive descent parser 
with AST generation. Code generation is not yet implemented.

A7 programs use the `.a7` file extension. See the `examples/` directory for 
sample programs demonstrating language features.

The language specification is in `docs/SPEC.md`. Implementation guidance for
this codebase is in `CLAUDE.md`.

## Dependencies

- Python 3.13+
- uv (for package management)
- pytest (for testing)
- rich (for terminal output)

The compiler is designed to target Zig as the output language.

This is work in progress. Contributions welcome.