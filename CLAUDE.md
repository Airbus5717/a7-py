# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **a7-py**, a Python implementation of the A7 programming language compiler/interpreter. A7 is a statically-typed, procedural programming language with C-style syntax, manual memory management, and compile-time generics.

## Key Commands

- **Install dependencies**: `uv sync` (use uv for dependency management)
- **Run the main program**: `python main.py` or `uv run python main.py`
- **Run with shell script**: `./run.sh` (activates venv and runs main)
- **Run Python with dependencies**: `uv run python <script>` 
- **Run Python tests**: `uv run pytest` (pytest is available as dependency)
- **Run specific test**: `uv run pytest path/to/test.py::SpecificTestClass::test_method -v`
- **Run tokenizer tests**: `uv run pytest test/test_tokenizer.py -v`
- **Test individual A7 programs**: Pass `.a7` file path as argument to interpreter (when implemented)

## Architecture

### Implementation Architecture
- **Compiler Pipeline**: Lexer → Parser → Code Generator (pluggable backends)
- **Main Entry**: `main.py` currently contains minimal implementation
- **Core Modules**:
  - `src/tokens.py`: Complete lexer/tokenizer with A7 token types
  - `src/compile.py`: Main compilation pipeline (A7Compiler class) 
  - `src/backends/`: Pluggable code generation backends (currently targets Zig, not C)
  - `src/errors.py`: Error handling infrastructure
- **Source files**: A7 programs use `.a7` extension
- **Default target**: Currently compiles to Zig (not C as originally planned)

### A7 Language Key Features
- **Statically typed** with type inference
- **Manual memory management** with `new`/`del` and `defer` statements  
- **Compile-time generics** via monomorphization using `$T` syntax
- **Two declaration operators**: `::` for constants, `:=` for variables
- **Logical operators**: Uses `and`/`or` keywords instead of `&&`/`||` symbols
- **Platform-aware types**: `isize`/`usize` for pointer-sized integers
- **Memory safety features**: bounds checking, lifetime tracking
- **File-based module system** with `pub` visibility
- **Function parameter immutability**: All parameters cannot be reassigned
- **Pointer semantics**: Modification through dereferencing with `ptr.*` syntax
- **Pattern matching**: `match` statements with explicit `fall` for fallthrough

### Critical A7 Language Details
- **Declaration syntax**: `::` creates immutable bindings, `:=` creates mutable bindings
- **Return statement**: Uses `ret` keyword (not `return`)
- **String type**: Built-in `string` type, ASCII-only encoding
- **Array/slice distinction**: Fixed arrays `[N]T` vs dynamic slices `[]T`
- **Reference syntax**: `ref T` for pointers, `&` for address-of, `ptr.*` for dereference
- **Generic constraints**: Type sets like `Numeric`, `Integer` defined with `@set()`
- **Import system**: `name :: import "module"` syntax

### A7 Language Examples Structure
The `examples/` directory contains A7 language examples showing language progression:
- `000_empty.a7` - Empty program
- `001_hello.a7` - Hello World with module imports
- `002_var.a7` - Variable/constant declarations with `::` and `:=`
- `003_comments.a7` - Comment syntax (single and multi-line)  
- `004_func.a7` - Function definitions and calls
- `005_for_loop.a7` - Loop constructs
- `006_if.a7` - Conditional statements
- `007_while.a7` - While loops
- `008_switch.a7` - Pattern matching with `match`
- `009_struct.a7` - Structure definitions
- `010_enum.a7` - Enumeration types
- `011_memory.a7` - Memory management with `new`/`del`
- `012_arrays.a7` - Array syntax and operations
- `013_pointers.a7` - Pointer semantics and dereferencing
- `014_generics.a7` - Generic type parameters and constraints
- `015_types.a7` - Type system features
- `016_unions.a7` - Union types
- `017_methods.a7` - Method definitions
- `018_modules.a7` - Module system usage
- `019_literals.a7` - Literal syntax (numbers, strings, chars)
- `020_operators.a7` - Operator precedence and usage
- `021_control_flow.a7` - Advanced control flow patterns

### Python Test Structure
The `test/` directory contains Python unit tests for the compiler:
- `test_tokenizer.py` - Comprehensive tokenizer tests paired with A7 examples
- `test_tokenizer_aggressive.py` - Additional tokenizer edge case tests

## Language Specification Reference

The complete A7 language specification is in `docs/SPEC.md` (2000+ lines). Key sections:
- **Section 2**: Lexical structure, keywords, operators
- **Section 3**: Type system (primitives, composites, generics)
- **Section 4**: Declaration syntax and expression categories
- **Section 5**: Control flow (if, match, loops, jumps)
- **Section 6**: Functions (declarations, parameters, methods, variadic)
- **Section 7**: Generic system with type parameters and constraints
- **Section 8**: Memory management (stack, heap, defer, safety)
- **Section 9**: Module system (imports, visibility, file-based)
- **Section 10**: Built-in functions and standard library
- **Section 11**: Token types and AST node structure
- **Section 12**: Complete grammar in EBNF

## Development Notes

- **Implementation Status**: 
  - ✅ Complete lexer/tokenizer with all A7 tokens (`src/tokens.py`)
  - ⚠️ Parser module referenced but not yet implemented (`src/parser.py` mentioned in compile.py)
  - ⚠️ Backend system partially implemented (base class exists, but missing concrete backends)
  - ❌ Main program only contains "Hello from a7-py!" placeholder
- **Missing Components**: Parser, AST nodes, concrete code generators, CLI argument handling
- **Target Language**: Currently designed to compile to Zig (see `src/compile.py` line 3: "A7 to Zig Compiler")
- **Development Philosophy**: Specification-driven development using `docs/SPEC.md` as authoritative reference

## Important Implementation Notes

- **Arrow operator removed**: The `->` operator was removed from the tokenizer as it's not used in the current A7 specification. Sequences like `->` are now tokenized as separate `MINUS` and `GREATER_THAN` tokens.
- **Tokenizer architecture**: The tokenizer in `src/tokens.py` handles all A7 tokens including nested comments, numeric literals (decimal, hex, binary), string/char literals with escapes, and operators with proper precedence handling.
- **Test structure**: Tests are organized with `test_tokenizer.py` covering A7 example files and `test_tokenizer_aggressive.py` for edge cases and error conditions.

## Dependencies

- **pytest**: Testing framework 
- **rich**: Enhanced terminal output and CLI formatting
- **Python 3.13+**: Minimum required Python version
- **uv**: Modern Python package manager for dependency management