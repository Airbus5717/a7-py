# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **a7-py**, a Python implementation of the A7 programming language compiler/interpreter. A7 is a statically-typed, procedural programming language with C-style syntax, manual memory management, and compile-time generics.

## Key Commands

- **Install dependencies**: `uv sync` (use uv for dependency management)
- **Run the main program**: `python main.py` or `uv run python main.py`
- **Run with shell script**: `./run.sh` (requires `chmod +x run.sh` first time, activates venv and uses uv run)
- **Run Python with dependencies**: `uv run python <script>` 
- **Run Python tests**: `uv run pytest` (pytest is available as dependency)
- **Run specific test**: `uv run pytest path/to/test.py::SpecificTestClass::test_method -v`
- **Run tokenizer tests**: `uv run pytest test/test_tokenizer.py -v`
- **Run error handling tests**: `uv run pytest test/test_tokenizer_errors.py -v`
- **Run all tokenizer tests**: `uv run pytest test/ -v` (includes basic, aggressive, and error tests)
- **Run parser tests**: `uv run pytest test/test_parser_basic.py -v` (basic parser functionality)
- **Run parser analysis**: `uv run pytest test/test_parser_integration.py::TestParserFailureAnalysis::test_analyze_all_examples -v -s` (comprehensive analysis)
- **Test individual A7 programs**: `uv run python main.py examples/001_hello.a7` (compiles and displays tokens/AST)
- **JSON output**: Add `--json` flag for structured output: `uv run python main.py examples/001_hello.a7 --json`

## Architecture

### Implementation Architecture
- **Compiler Pipeline**: Lexer → Parser → Code Generator (pluggable backends)
- **Main Entry**: `main.py` contains CLI argument parsing and calls compile pipeline
- **Core Modules**:
  - `src/tokens.py`: Complete lexer/tokenizer with A7 token types and length validation
  - `src/parser.py`: Recursive descent parser with precedence climbing for expressions
  - `src/ast_nodes.py`: Complete AST node system with 79 node kinds and utility functions
  - `src/compile.py`: Main compilation pipeline (A7Compiler class) with tokenization → parsing → AST generation
  - `src/backends/`: Pluggable code generation backends (base class exists, concrete backends pending)
  - `src/errors.py`: Comprehensive error handling with 17 specific error types, advice messages, and Rich-formatted display
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

**Tokenizer Tests:**
- `test_tokenizer.py` - Comprehensive tokenizer tests paired with A7 examples
- `test_tokenizer_aggressive.py` - Additional tokenizer edge case tests
- `test_tokenizer_errors.py` - Comprehensive error handling and error message formatting tests

**Parser Tests (NEW):**
- `test_parser_basic.py` - Core parser functionality tests (constants, variables, functions, expressions, types)
- `test_parser_missing_constructs.py` - Documents missing language features with skip markers (structs, enums, unions, match, defer)
- `test_parser_examples.py` - Tests parser against actual A7 example files with failure analysis
- `test_parser_edge_cases.py` - Edge cases, error recovery, robustness, and boundary condition tests
- `test_parser_integration.py` - Integration tests and comprehensive analysis of parser capabilities

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
  - ✅ Complete lexer/tokenizer with all A7 tokens including `$` for generics (`src/tokens.py`)
  - ✅ Advanced character literal parsing with hex escape sequences (`\x41`)
  - ✅ JSON output format with `--json` flag for structured data export
  - ✅ Comprehensive error handling system (17 error types) with helpful advice
  - ✅ Enhanced error display: Rich-formatted output with visual context, dynamic error indicators (`▲` for single chars, `└──┘` for spans), compact `[line X: col X]` format, and contextual hints
  - ✅ Length validation for identifiers (100 chars) and numbers (100 digits)
  - ✅ Tab detection with specific error messages
  - ✅ All 22 A7 examples now tokenize successfully (was 19/22, now 22/22)
  - ✅ **Recursive descent parser implemented** (`src/parser.py`) with precedence climbing for expressions
  - ✅ **Complete AST node system** (`src/ast_nodes.py`) with 79 node kinds and utility functions
  - ✅ **Enhanced compilation pipeline** now supports tokenization → parsing → AST generation
  - ✅ **Comprehensive parser test suite** (100+ test cases across 5 test files covering functionality, missing features, examples, edge cases)
  - ⚠️ Backend system partially implemented (base class exists, but missing concrete backends)
  - ✅ Main program has CLI parsing and calls compilation pipeline
  - ✅ Compilation outputs Rich console display or JSON format with AST information
- **Missing Components**: Concrete code generator backends (lexing and parsing complete)
- **Target Language**: Currently designed to compile to Zig (see `src/compile.py` line 3: "A7 to Zig Compiler")
- **Development Philosophy**: Specification-driven development using `docs/SPEC.md` as authoritative reference

## Important Implementation Notes

- **Generics support**: The `$` token is fully implemented for generic type parameters (`$T`, `$U`) as specified in the A7 language
- **Advanced character literals**: Supports all escape sequences including hex escapes (`\x41`) with proper validation
- **JSON output**: Added `--json` flag providing structured output with metadata, source code, and token arrays for tooling integration
- **Arrow operator removed**: The `->` operator was removed from the tokenizer as it's not used in the current A7 specification. Sequences like `->` are now tokenized as separate `MINUS` and `GREATER_THAN` tokens.
- **Tokenizer architecture**: The tokenizer in `src/tokens.py` handles all A7 tokens including nested comments, numeric literals (decimal, hex, binary), string/char literals with escapes, and operators with proper precedence handling.
- **Enhanced error system**: `src/errors.py` implements 17 specific error types (e.g., `INVALID_CHARACTER`, `NOT_CLOSED_STRING`, `TABS_UNSUPPORTED`) with corresponding helpful advice messages and precise error location tracking.
- **Error message format**: Uses format `error: message, line: x, col: y` followed by `help: advice` with yellow line numbers, white code, and red `^` pointers for precise error indication.
- **Smart context display**: Small files (≤5 lines) show all lines, larger files show contextual lines around errors.
- **Test structure**: Tests are organized with `test_tokenizer.py` covering A7 example files, `test_tokenizer_aggressive.py` for edge cases, and `test_tokenizer_errors.py` for comprehensive error handling validation.
- **Complete example coverage**: All 22 A7 example files now tokenize successfully, including complex generics and character literals

## Dependencies

- **Python 3.13+**: Minimum required Python version
- **uv**: Modern Python package manager for dependency management
- **pytest**: Testing framework with comprehensive test suite (100+ tests)
- **rich**: Enhanced terminal output, error formatting, and CLI display

## Error Handling System

The error system provides professional-grade error reporting with:
- **Visual Context**: Source code display with line numbers and error highlighting
- **Dynamic Indicators**: Triangle (`▲`) for single characters, box drawing (`└──┘`) for spans
- **Compact Location**: Format `[line X: col X]` for precise error positioning
- **Contextual Hints**: Helpful suggestions for fixing common errors
- **Rich Formatting**: Clean, readable output without distracting elements

## Current Implementation Status

**CURRENT STATUS (January 2025)**: The compiler has **complete lexing and parsing capabilities**:

- ✅ **Lexer/Tokenizer**: Fully implemented, handles all A7 tokens, passes all tests
- ✅ **Parser Core**: **100% A7 example success rate** - all 22 example files parse successfully
- ✅ **Language Features**: All major A7 constructs implemented (struct, enum, union, match, defer, generics, pointers)
- ✅ **AST System**: 79 node kinds implemented covering all A7 language constructs  
- ✅ **Error Handling**: Enhanced Rich-formatted error display with visual indicators and context
- ✅ **CLI Interface**: Full argument parsing with `--json` output option
- ⚠️ **Expression Gaps**: Array literals, struct initialization, cast expressions not fully implemented
- ⚠️ **Code Generation**: Base backend class exists, but no concrete Zig backend implemented

**Next Development Priority**: Implement Zig code generator backend for complete compilation pipeline.

## Parser Implementation Analysis

### Parser Capabilities (WORKING)
- ✅ **Basic Declarations**: Constants (`::`) and variables (`:=`) with type inference
- ✅ **Function Declarations**: With parameters, return types, and body parsing
- ✅ **Expression Parsing**: Binary/unary operators with correct precedence
- ✅ **Control Flow**: if/else statements, while loops, basic for loops
- ✅ **Type System**: Primitive types, arrays `[N]T`, slices `[]T`, pointers `ref T`
- ✅ **Function Calls**: With argument lists and nested calls
- ✅ **Import Statements**: Basic `import "module"` syntax
- ✅ **Literals**: All literal types (integers, floats, strings, chars, booleans, nil)
- ✅ **Error Recovery**: Basic synchronization at statement/declaration boundaries

### Parser Implementation Status (January 2025)

**COMPREHENSIVE LANGUAGE SUPPORT**: All major A7 language features are successfully parsed:

### Fully Implemented Language Constructs ✅
- ✅ **All Declaration Types**: Constants (`::`) and variables (`:=`) with full type support
- ✅ **Complete Type System**: Primitives, arrays `[N]T`, slices `[]T`, pointers `ref T`, generics `$T`
- ✅ **Advanced Data Types**: Struct, enum, union declarations with full member support
- ✅ **Function System**: Declarations, parameters, return types, generic functions
- ✅ **Control Flow**: if/else, while, for loops, match statements, defer
- ✅ **Expression Parsing**: Binary/unary operators with correct precedence, function calls
- ✅ **Memory Management**: `new`, `del` keywords and pointer operations
- ✅ **Module System**: Import statements and public visibility
- ✅ **All Example Files**: 22/22 A7 examples parse successfully with 100% success rate

### Minor Implementation Gaps ⚠️
- ⚠️ **Array Literals**: `[1, 2, 3]` syntax in expressions
- ⚠️ **Struct Initialization**: `Person{name: "John"}` syntax
- ⚠️ **Cast Expressions**: `cast(type, value)` syntax
- ⚠️ **Named Imports**: `name :: import "module"` syntax
- ⚠️ **Explicit Type Annotations**: `var: type := value` syntax


### Test Coverage
- **Comprehensive Test Suite**: 100+ test cases across tokenizer, parser, and error handling
- **Example Integration**: All 22 A7 example files parse successfully (100% success rate)
- **Edge Cases**: Robust testing for error conditions, boundary cases, and recovery scenarios
- **Analysis Tools**: Automated parser capability analysis and language feature detection

### Development Priorities
1. **High Priority - Code Generation**:
   - Implement concrete Zig backend in `src/backends/`
   - Add code generation for all AST node types
   - Complete the compilation pipeline from A7 source to Zig output
2. **Medium Priority - Expression Enhancements**:
   - Implement array literals `[1, 2, 3]` in `parse_primary_expression`
   - Implement struct initialization `Person{name: "John"}` syntax
   - Implement cast expressions `cast(type, value)`
3. **Low Priority - Language Refinements**:
   - Add named imports: `name :: import "module"`
   - Add explicit type annotations: `var: type := value`
   - Enhanced error recovery for edge cases
