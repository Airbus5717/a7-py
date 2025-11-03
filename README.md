# A7 Programming Language Compiler

A Python-based compiler for A7, a statically-typed systems programming language. A7 combines the simplicity of C-style syntax with modern features like generics, type inference, and property-based pointer operations.

The compiler currently includes a complete tokenizer and parser (411 tests passing!). Code generation to Zig is planned.

## Inspired By

A7 draws inspiration from practical systems programming languages that prioritize clarity and programmer productivity:

- **[JAI](https://www.youtube.com/playlist?list=PLmV5I2fxaiCKfxMBrNsU1kgKJXD3PkyxO)** by Jonathan Blow - Design philosophy and compile-time features
- **[Odin](https://odin-lang.org/)** by Ginger Bill - Simplicity and explicit memory management

## Quick Start

**Requirements:** Python 3.13+ and [uv](https://docs.astral.sh/uv/) (recommended package manager)

```bash
# Install uv (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/macOS
# or: pip install uv

# Clone and setup
git clone <repository-url>
cd a7-py
uv sync
```

## Usage

Compile an A7 program:
```bash
uv run python main.py examples/001_hello.a7
# or use the shell script: ./run.sh examples/001_hello.a7
```

Run tests:
```bash
uv run pytest                          # All tests (411 passing!)
uv run pytest test/test_tokenizer.py  # Specific test file
```

## What Works

The parser handles most A7 language features:

- **Types**: Primitives, arrays, slices, pointers, generics, function types, inline structs
- **Declarations**: Functions, structs, enums, unions, variables, constants
- **Control Flow**: if/else, while, for loops, match statements
- **Expressions**: All operators with proper precedence, casts, literals
- **Memory**: Property-based pointer syntax (`.adr`, `.val`), new/delete
- **Imports**: Module system with named imports
- **Error Messages**: Rich formatting with source context

**Test Coverage**: 411 tests passing, covering edge cases and complex type combinations

## What's Next

- Code generation to Zig
- Type checking and semantic analysis
- Standard library

## Learn More

- `docs/SPEC.md` - Language specification
- `examples/` - 36 sample programs including practical applications
- `CLAUDE.md` - Development guide

---

Work in progress. Contributions welcome!