# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an A7 programming language compiler implemented in Python. A7 is a statically-typed, procedural language designed for AI and systems programming with array programming capabilities, generics, and manual memory management. The compiler targets Zig as the output language.

## Core Architecture

### Compilation Pipeline
The compiler follows a standard multi-stage architecture:

1. **Lexical Analysis** (`src/tokens.py`) - Tokenizes A7 source code with comprehensive error reporting
2. **Syntax Analysis** (`src/parser.py`) - Recursive descent parser that builds ASTs
3. **AST Construction** (`src/ast_nodes.py`) - Defines all AST node types and factory functions
4. **Error Handling** (`src/errors.py`) - Rich error formatting with 17+ specific error types
5. **Code Generation** (`src/backends/`) - Backend interface (Zig target planned)
6. **Main Pipeline** (`src/compile.py`) - Orchestrates the entire compilation process

### Key Components

**Tokenizer** (`src/tokens.py`, ~765 lines):
- Handles all A7 tokens including generics (`$T`), array syntax, and operators
- Validates identifier/number length limits (100 chars each)
- Provides detailed error locations and helpful messages
- Supports hex escapes (`\x41`), nested comments, and all A7 literals

**Parser** (`src/parser.py`, ~1137 lines):
- Recursive descent with precedence climbing for expressions
- Builds complete ASTs for all A7 language constructs
- Handles generics, functions, structs, enums, control flow
- Currently parses 16 of 22 A7 example programs successfully (72% success rate)

**AST Nodes** (`src/ast_nodes.py`, ~558 lines):
- Enum-based design with minimal inheritance
- Factory functions for consistent node creation
- Supports all A7 constructs: generics, memory management, pattern matching

**Error System** (`src/errors.py`, ~461 lines):
- Rich console formatting with syntax highlighting
- 17 specific lexer error types with helpful advice
- Source location tracking with line/column precision
- Both human-readable and JSON output modes

## Development Commands

### Core Compilation
```bash
# Compile A7 source files
uv run python main.py examples/001_hello.a7
uv run python main.py --json examples/014_generics.a7    # JSON output
./run.sh examples/021_control_flow.a7                    # Alternative

# Debugging and analysis modes
uv run python main.py examples/006_if.a7 --tokenize-only        # Show tokenization output only
uv run python main.py examples/004_func.a7 --parse-only         # Show tokenization + parsing output  
uv run python main.py examples/002_var.a7 --tokenize-only --json # JSON analysis output

# Test all examples
for file in examples/*.a7; do uv run python main.py "$file" || echo "FAILED: $file"; done
```

### Testing (238 total tests)
```bash
# Run all tests
uv run pytest

# Test specific components
uv run pytest test/test_tokenizer.py              # Core tokenizer tests
uv run pytest test/test_parser_basic.py           # Basic parser functionality  
uv run pytest test/test_tokenizer_errors.py       # Error handling validation
uv run pytest test/test_parser_examples.py        # All 22 A7 examples

# Run single test method
uv run pytest test/test_tokenizer.py::TestTokenizer::test_keywords -v

# Test with coverage
uv run pytest --tb=short -v                       # Shorter tracebacks
```

### Development Environment
```bash
uv sync                           # Install dependencies
uv add <package>                  # Add dependency  
uv tree                          # Show dependency tree
```

## Testing Strategy

The project uses a 3-tier testing approach:

1. **Basic Functionality** - Core language features work correctly
2. **Aggressive Edge Cases** - Boundary conditions, malformed input, limits
3. **Error Handling** - All error types produce helpful messages

### Test Organization
- `test_tokenizer.py` - Token type validation for all A7 constructs
- `test_tokenizer_aggressive.py` - Edge cases, limits, malformed syntax
- `test_tokenizer_errors.py` - Error message validation (17 error types)
- `test_parser_*.py` - Parser functionality across language features
- `test_parser_examples.py` - Integration tests using all 22 A7 examples

### A7 Example Coverage
The `examples/` directory contains 22 A7 programs demonstrating:
- `000_empty.a7` through `021_control_flow.a7`
- All major language features: functions, generics, memory management, structs, enums
- These serve as both documentation and integration tests

## Language Implementation Status

### ✅ Completed
- **Complete tokenizer** with all A7 token types
- **Recursive descent parser** handling all language constructs  
- **AST generation** for the full A7 grammar
- **Error system** with 17+ specific error types and rich formatting
- **JSON output mode** for tooling integration
- **6 of 22 A7 examples** parse completely successfully (27% success rate, see Missing Parser Features section for detailed breakdown)

### 🚧 In Development
- **Parser improvements** for remaining A7 constructs (struct literals, imports, for loops, switch statements)  
- **Code generation** to Zig (backend architecture exists)
- **Type checking** and semantic analysis
- **Optimization passes**

### 🎯 Key Design Decisions
- **Enum-based AST** nodes for simplicity and performance
- **Factory pattern** for AST construction with validation
- **Rich error formatting** prioritizes developer experience  
- **uv-based** dependency management for modern Python workflows
- **Comprehensive testing** with 238 tests covering edge cases

## A7 Language Features

This compiler implements the A7 language specification (`docs/SPEC.md`) including:

- **Static typing** with type inference and generics (`$T`)
- **Array programming** with broadcasting and vectorized operations
- **Memory management** (`new`/`del`, pointers, slices)
- **Pattern matching** (`match`/`case` with fallthrough)
- **Modules** with visibility controls (`pub`)
- **Functions** with immutable parameters and generic constraints
- **Composite types** (structs, unions, enums, arrays)

The compiler uses `uv` for dependency management and pytest for testing. All development should use `uv run` prefix for consistency.

## Parser Architecture & Context Handling

**Context-Aware Parsing**: The parser includes sophisticated context detection to handle ambiguous syntax:
- **Struct Literal Detection** (`_should_parse_struct_literal()`) - Distinguishes `identifier{` between struct literals and statement blocks
- **Expression vs Statement Context** - Prevents misinterpreting `if condition {` where the `{` starts a block, not a struct literal
- **Error Recovery** - Parser continues after errors to provide comprehensive feedback, but may misclassify some constructs

**Missing Parser Features** (7 major areas causing example failures):

1. **Import + Field Access Chain** (`examples/001_hello.a7`, `002_var.a7`):
   - `io :: import "std/io"` followed by `io.println()` fails
   - Field access on imported modules not implemented
   - Module namespace resolution missing

2. **For Loop Variants** (`examples/005_for_loop.a7`):  
   - Range-based loops: `for value in arr` not implemented
   - Indexed iteration: `for i, value in arr` not implemented
   - Only simple infinite loops `for { ... }` currently work

3. **Match/Switch Statements** (`examples/008_switch.a7`):
   - Basic `match` parsing exists but complex patterns fail
   - Range patterns `case 6..10:` not supported
   - Multiple case values `case 3, 4, 5:` not supported  
   - `fall` (fallthrough) statement not implemented

4. **Struct Literal Initialization** (`examples/009_struct.a7`):
   - Anonymous initialization: `Token{1, [10, 20, 30]}` fails
   - Named field initialization: `Person{name: "John", age: 30}` works in simple cases
   - Array field initialization in struct literals fails
   - Nested struct initialization not supported
   - Local struct declarations inside functions fail

5. **Enum Declarations & Access** (`examples/010_enum.a7`):
   - Enum declaration parsing implemented but access patterns fail
   - Scoped enum access: `TknType.Id` not supported
   - Explicit enum values: `Ok = 200` not fully implemented
   - `cast(i32, status)` expressions not supported

6. **Memory Management Syntax** (`examples/011_memory.a7`):
   - `new` expressions for allocation not implemented
   - `defer` statements parsed but not integrated with scopes
   - Pointer dereference: `ptr.*` syntax not supported  
   - `del` statements for deallocation not implemented

7. **Advanced Type Features**:
   - Explicit type annotations: `c: i32 := 3` fail parsing
   - Function types in parameters not implemented (TODO comment exists)
   - Array literals with explicit types: `[3]i32 = [10, 20, 30]` fail

## CLI Debugging Features

The A7 compiler provides specialized flags for analyzing source code at different stages:

### Analysis Modes
- `--tokenize-only` - Show lexical analysis (tokenization) output only, skip parsing
- `--parse-only` - Show tokenization and syntax analysis (AST generation), skip code generation
- `--json` - Output results in JSON format (compatible with both analysis modes)
- `--verbose` - Show detailed compilation progress information

### Usage Examples
```bash
# Tokenization analysis with rich visual output
uv run python main.py examples/006_if.a7 --tokenize-only

# Parsing analysis showing AST structure
uv run python main.py examples/014_generics.a7 --parse-only

# JSON output for tooling integration
uv run python main.py examples/009_struct.a7 --parse-only --json

# Combine with verbose for detailed progress
uv run python main.py examples/021_control_flow.a7 --parse-only --verbose
```

### AST Visualization Features
The `--parse-only` mode displays AST structure with:
- **Technical node names** (FUNCTION, VAR, IF_STMT, WHILE, etc.)
- **Inline parameters** for functions: `FUNCTION main (x, y)`  
- **Statement hierarchies** showing actual nested structures (IF_STMT containing EXPRESSION_STMT, VAR declarations)
- **Clean tree format** without redundant "Then/Else" nodes

These modes are useful for:
- Understanding tokenization issues in A7 source code
- Debugging parser behavior and AST generation
- Analyzing language constructs and their representation
- Integrating with external tools via JSON output
- Learning A7 language structure and syntax

## Specialized Agents

Use `/task compiler-test-engineer` for:
- Adding test coverage for new language features
- Testing edge cases in tokenizer/parser
- Validating error message quality
- Ensuring A7 examples continue working

## Parser Development Workflow

When implementing missing parser features:

1. **Identify the construct** - Use failing examples to pinpoint exact syntax
2. **Check tokenization** - Run `--tokenize-only` to ensure tokens are correct
3. **Add parsing method** - Follow existing pattern in `src/parser.py`  
4. **Update AST nodes** - Add new node types to `src/ast_nodes.py` if needed
5. **Test incrementally** - Run specific example with `--parse-only` to debug
6. **Add comprehensive tests** - Cover edge cases in appropriate test file

**Key parsing patterns**:
- `parse_*_statement()` for control flow (if, while, for, match)  
- `parse_*_expression()` for values and operations
- `parse_*_decl()` for top-level declarations (struct, enum, function)
- Use `create_span_from_token()` for accurate error locations
- Follow precedence climbing for expressions