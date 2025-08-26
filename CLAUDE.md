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

**Tokenizer** (`src/tokens.py`, ~902 lines):
- Handles all A7 tokens including single-token generics (`$T`, `$TYPE`, `$MY_TYPE`), array syntax, and operators
- Validates generic patterns: only letters and underscores after `$` (enforced at tokenization)
- Validates identifier/number length limits (100 chars each)
- Provides detailed error locations and helpful messages
- Supports hex escapes (`\x41`), nested comments, and all A7 literals
- Comprehensive assignment operators including bitwise (&=, |=, ^=, <<=, >>=)

**Parser** (`src/parser.py`, ~1602 lines):
- Recursive descent with precedence climbing for expressions
- Builds complete ASTs for all A7 language constructs
- Handles generics with single GENERIC_TYPE tokens (`$T`, `$TYPE`, `$MY_TYPE`)
- Mixed parameter parsing for functions with both generics and regular parameters
- Context-aware struct literal detection vs statement blocks
- Currently parses most basic A7 constructs successfully

**AST Nodes** (`src/ast_nodes.py`, ~552 lines):
- Enum-based design with minimal inheritance
- Factory functions for consistent node creation
- Supports all A7 constructs: generics, memory management, pattern matching
- Token-to-operator mapping for all assignment types

**Error System** (`src/errors.py`, ~516 lines):
- Rich console formatting with syntax highlighting
- 18+ specific lexer error types with helpful advice (including generic syntax validation)
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

### Testing (301 total tests, ~5900 lines)
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
- **Complete tokenizer** with all A7 token types and proper comment handling
- **Recursive descent parser** handling most A7 language constructs  
- **AST generation** for core A7 grammar
- **Error system** with 18+ specific error types and rich formatting
- **JSON output mode** for tooling integration
- **Mixed parameter parsing** for functions combining generics (`$T`) and regular parameters in same parentheses
- **Struct field parsing** with proper terminator handling for multiline declarations
- **Type annotation support** for both inferred (`c := 3`) and explicit (`c: i32 = 3`) syntax
- **Import statement parsing** with named imports (`io :: import "std/io"`)
- **Field access chains** working correctly (`io.println("Hello")`)
- **Struct literal initialization** supporting both positional (`Token{1, [10, 20, 30]}`) and named (`Person{name: "John"}`) styles
- **Local struct declarations** inside function bodies
- **All assignment operators** including bitwise operations (&=, |=, ^=, <<=, >>=)
- **Generic type validation** at tokenization level (only letters/underscores after `$`)

### 🚧 In Development
- **Parser improvements** for remaining A7 constructs (for loop variants, complex match patterns, enum access patterns)  
- **Code generation** to Zig (backend architecture exists)
- **Type checking** and semantic analysis
- **Optimization passes**

### 🎯 Key Design Decisions
- **Enum-based AST** nodes for simplicity and performance
- **Factory pattern** for AST construction with validation
- **Rich error formatting** prioritizes developer experience  
- **uv-based** dependency management for modern Python workflows
- **Comprehensive testing** with 301 tests covering edge cases across 5900+ lines of test code

## A7 Language Features

This compiler implements the A7 language specification (`docs/SPEC.md`) including:

- **Static typing** with type inference and generics (`$T`)
- **Array programming** with broadcasting and vectorized operations
- **Memory management** (`new`/`del`, property-style pointers with `variable.adr` and `ptr.val`, slices)
- **Pattern matching** (`match`/`case` with fallthrough)
- **Modules** with visibility controls (`pub`)
- **Functions** with immutable parameters and generic constraints
- **Composite types** (structs, unions, enums, arrays)

The compiler uses `uv` for dependency management and pytest for testing. All development should use `uv run` prefix for consistency.

## A7 Pointer Syntax

A7 uses an intuitive property-based pointer syntax instead of traditional C-style operators:

**Address-of Operation:**
```a7
// Traditional C: ptr = &variable
// A7: 
ptr := variable.adr
```

**Dereference Operation:**
```a7
// Traditional C: value = *ptr
// A7:
value := ptr.val
```

**Assignment through pointer:**
```a7
// Traditional C: *ptr = 42
// A7:
ptr.val = 42
```

**Multiple indirection:**
```a7
// Traditional C: value = ***ptr_ptr_ptr
// A7:
value := ptr_ptr_ptr.val.val.val
```

This syntax is:
- **More intuitive**: `.adr` and `.val` are self-documenting
- **Consistent**: Follows property access patterns used elsewhere
- **Clear**: No ambiguity about operation being performed
- **Beginner-friendly**: Reads like natural language

## Parser Architecture & Context Handling

**Context-Aware Parsing**: The parser includes sophisticated context detection to handle ambiguous syntax:
- **Struct Literal Detection** (`_should_parse_struct_literal()`) - Distinguishes `identifier{` between struct literals and statement blocks
- **Expression vs Statement Context** - Prevents misinterpreting `if condition {` where the `{` starts a block, not a struct literal
- **Error Recovery** - Parser continues after errors to provide comprehensive feedback, but may misclassify some constructs

**Parser Success Status**: The parser now successfully handles:
- ✅ **Basic examples** (`000_empty.a7`, `001_hello.a7`, `002_var.a7`, `003_comments.a7`, `004_func.a7`, `005_for_loop.a7`)
- ✅ **Struct features** (`009_struct.a7`) with both positional and named initialization
- ✅ **Import statements** with field access chains (`io :: import "std/io"` followed by `io.println()`)
- ✅ **Local type declarations** inside function bodies

**Remaining Parser Features** (4 major areas still needing implementation):

1. **For Loop Variants** (`examples/005_for_loop.a7`):  
   - Range-based loops: `for value in arr` not implemented
   - Indexed iteration: `for i, value in arr` not implemented
   - Only simple infinite loops `for { ... }` currently work

2. **Complex Match/Switch Patterns** (`examples/008_switch.a7`):
   - Range patterns `case 6..10:` not supported
   - Multiple case values `case 3, 4, 5:` not supported  
   - `fall` (fallthrough) statement not implemented

3. **Enum Access Patterns** (`examples/010_enum.a7`):
   - Scoped enum access: `TknType.Id` not supported
   - `cast(i32, status)` expressions not supported

4. **Memory Management Expressions** (`examples/011_memory.a7`):
   - `new` expressions for allocation not implemented
   - `del` statements for deallocation not implemented

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

## Test Status and Debugging

### Current Test Status (as of latest fixes)
- **238 passing tests** out of 301 total 
- **23 failing tests** (mostly expecting `ParseError` but getting successful parsing)
- **40 skipped tests** (features not yet implemented)

### Common Test Failure Patterns
Most failures are tests expecting errors that now succeed due to parser improvements:
- Tests expecting `ParseError` for complex syntax that parser now handles
- Struct literal parsing vs statement block disambiguation working better
- Assignment operator coverage now complete

### Debugging Failed Tests
```bash
# Run specific failing test for detailed output
uv run pytest test/test_parser_comprehensive_problems.py::TestStructLiteralComplexPatterns::test_nested_struct_initialization -v

# Run all tests in quiet mode to see failure summary
uv run pytest --tb=line -q

# Check if a specific A7 example compiles successfully  
uv run python main.py examples/009_struct.a7 --parse-only
```

## Specialized Agents

Use `/task compiler-test-engineer` for:
- Adding test coverage for new language features
- Testing edge cases in tokenizer/parser
- Validating error message quality
- Ensuring A7 examples continue working
- Updating tests to reflect improved parser capabilities

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


