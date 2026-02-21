# A7 Programming Language Compiler

A Python-based compiler for A7, a statically-typed systems programming language. A7 combines the simplicity of C-style syntax with modern features like generics, type inference, and property-based pointer operations.

The compiler features a complete pipeline: tokenizer, parser, 3-pass semantic analysis, AST preprocessing, and Zig code generation.

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

Compile an A7 program to Zig:
```bash
uv run python main.py examples/001_hello.a7
# Output: examples/001_hello.zig
```

Modes and output formats:
```bash
uv run python main.py --mode tokens examples/006_if.a7                     # Tokens only
uv run python main.py --mode ast examples/004_func.a7                      # Tokens + AST
uv run python main.py --mode semantic examples/009_struct.a7               # Through semantic passes
uv run python main.py --mode pipeline examples/014_generics.a7             # Full pipeline, no file write
uv run python main.py --format json examples/014_generics.a7               # Machine-readable JSON
uv run python main.py examples/001_hello.a7 --mode compile --doc-out auto  # Compile + auto docs
uv run python main.py examples/001_hello.a7 --mode compile --doc-out out.md  # Compile + custom docs
uv run python main.py --mode doc examples/001_hello.a7                     # Doc-only run
uv run python main.py --verbose examples/009_struct.a7                     # Full pipeline details
```

Exit codes for automation:
```text
0 success, 2 usage, 3 io, 4 tokenize, 5 parse, 6 semantic, 7 codegen, 8 internal
```

Run tests:
```bash
PYTHONPATH=. uv run pytest                         # All tests
PYTHONPATH=. uv run pytest test/test_tokenizer.py  # Specific test file
PYTHONPATH=. uv run pytest -k "generic" -v         # Targeted tests
uv run python scripts/verify_examples_e2e.py       # Compile/build/run + output checks for all examples
```

## Compilation Pipeline

```
Source (.a7) → Tokenizer → Parser → Semantic Analysis (3-pass) → AST Preprocessing → Zig Codegen → Output (.zig)
```

1. **Tokenizer** — Lexes source into tokens. Handles single-token generics (`$T`), nested comments, all number formats.
2. **Parser** — Recursive descent with precedence climbing. Parses all A7 constructs.
3. **Semantic Analysis** — Name resolution, type checking with inference, control flow validation.
4. **AST Preprocessing** — 9 sub-passes: sugar lowering, stdlib resolution, mutation/usage analysis, type inference, shadowing resolution, function hoisting, constant folding.
5. **Zig Code Generation** — Translates AST to valid Zig source code.

All AST traversals are iterative (no recursion) — the pipeline works with Python's recursion limit set to 100.

## What Works

- **Types**: Primitives, arrays, slices, pointers, generics, function types, inline structs
- **Declarations**: Functions, structs, enums, unions, variables, constants, type aliases
- **Control Flow**: if/else, while, for loops, for-in, match statements, defer
- **Expressions**: All operators with proper precedence, casts, if-expressions, struct/array literals
- **Memory**: Property-based pointer syntax (`.adr`, `.val`), new/delete, defer cleanup
- **Imports**: Module system with named imports, using imports, aliased imports
- **Generics**: Type parameters (`$T`), constraints, type sets, generic structs
- **Code Generation**: Full A7 → Zig translation with smart var/const inference, function hoisting, shadowing prevention
- **Standard Library**: Registry with io and math modules, backend-specific mappings
- **Error Messages**: Rich formatting with source context and structured error types

## Project Status

- **983 tests passing**, 9 skipped
- **36/36 examples** pass end-to-end compile + build + run + golden-output verification
- Parser is 100% complete for the A7 specification
- Zig backend handles all AST node types

## Learn More

- `docs/SPEC.md` - Language specification
- `examples/` - 36 sample programs
- `CLAUDE.md` - Development guide
- `MISSING_FEATURES.md` - Feature status and roadmap
- `CHANGELOG.md` - Change history

---

Work in progress. Contributions welcome!
