# A7 Programming Language Compiler

This is a Python implementation of a compiler for the A7 programming language.
A7 is a statically-typed, procedural language with C-style syntax, manual 
memory management, and compile-time generics.

**Current Status**: The compiler has a complete tokenizer and a working recursive 
descent parser that generates ASTs for most A7 language constructs. Code generation 
to Zig is planned but not yet implemented.

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

Run the full test suite:
```bash
uv run pytest
```

Run specific tests:
```bash
uv run pytest test/test_tokenizer.py -v
uv run pytest test/test_parser_basic.py -v
```

**Test Status**: 264 passing tests, 0 failing, 37 skipped

## Features

### Currently Implemented
- ✅ Complete tokenizer with all A7 token types
- ✅ Recursive descent parser with AST generation
- ✅ Function declarations with generics
- ✅ Variable and constant declarations
- ✅ Control flow (if/else, while, for loops, match statements)
- ✅ Expressions with proper operator precedence
- ✅ Struct, enum, and union declarations
- ✅ Cast expressions (`cast(type, value)`)
- ✅ Import statements
- ✅ Rich error messages with source context

### In Development
- 🚧 Code generation to Zig
- 🚧 Type checking and semantic analysis
- 🚧 Standard library implementation

## Documentation

- **Language Specification**: `docs/SPEC.md` - Complete A7 language design
- **Implementation Guide**: `CLAUDE.md` - Detailed status and development guidance
- **Examples**: `examples/` directory - 22 sample A7 programs

## Dependencies

- Python 3.13+
- uv (for package management)
- pytest (for testing)
- rich (for terminal output)

The compiler is designed to target Zig as the output language.

This is work in progress. Contributions welcome.