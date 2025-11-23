# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A7 programming language compiler implemented in Python. A7 is a statically-typed, procedural language with array programming capabilities, generics, and manual memory management. The compiler targets Zig as the output language.

## Project Status

**Current Test Results**: 465/481 parser tests + 98/228 semantic tests passing ✅
- ✅ **Tokenizer**: 100% Complete - all token types, escape sequences, number formats
- ✅ **Parser**: 97% Complete - Nearly all language features implemented!
- ✅ **AST**: Complete AST generation for entire language
- 🚀 **Semantic Analysis**: INTEGRATED INTO COMPILATION PIPELINE! (Phase 2)
  - ✅ Type system with all A7 types
  - ✅ Symbol tables with hierarchical scoping
  - ✅ Name resolution pass - FULLY INTEGRATED
  - ✅ Type checking pass - INTEGRATED (expression inference in progress)
  - ✅ Semantic validation pass - INTEGRATED
  - ✅ Generic type infrastructure
  - ✅ Module resolution system
  - ✅ Error detection and rich formatting
  - 📊 98/228 tests passing (43% - foundation complete, type inference in progress)
- 🚧 **Code Generation**: Not yet implemented (next phase)

**⏸️ Deferred Features**:
- **Labeled loops** - DEFERRED due to syntax ambiguity (`label: type` vs `variable: type`)
  - AST has `label` field reserved for future use
  - Requires syntax redesign or sophisticated lookahead

**🎉 Recently Implemented Parser Features**:
- ✅ **Variadic functions** (`fn(values: ..i32)`, `fn(args: ..)`)
- ✅ **Type sets** (`@type_set(i32, i64, f32)` and constraints)
- ✅ **Generic constraints** (`$T: Numeric`, `$T: @type_set(...)`)
- ✅ **Builtin intrinsics** (`@size_of(T)`, `@align_of(T)`, `@type_id(T)`, etc.)
- ✅ **Using imports** (`using import "module"`)
- ✅ **Named item imports** (`import "vector" { Vec3, dot }`)
- ✅ **Generic struct literal instantiation** (`Pair(i32, string){42, "answer"}`)

**Previously Completed Features**:
- ✅ Inline/anonymous struct types (`struct { id: i32, data: string }`)
- ✅ Function type parsing (`fn(i32) i32`, function pointers)
- ✅ Generic type instantiation (`List($T)`, `Map(K, V)`)
- ✅ All control flow constructs (if/else, while, for, match)
- ✅ Memory management (new/del/defer)
- ✅ Complex type expressions (arrays, slices, pointers)
- ✅ All operators (arithmetic, comparison, bitwise, assignment)

**Key Documentation**:
- **`CHANGELOG.md`** - Track all changes here! Update for every feature/fix
- **`MISSING_FEATURES.md`** - Comprehensive feature gap analysis
  - Feature completeness by category
  - Priority ranking (P0 critical → P3 future)
  - Implementation roadmap
  - Dependency graphs and risk assessment
- **`docs/SPEC.md`** - Complete A7 language specification
- **`examples/README.md`** - Catalog of all example programs

**IMPORTANT**: When adding new features or fixing bugs, always update:
1. `CHANGELOG.md` - Add entry under [Unreleased] section
2. `MISSING_FEATURES.md` - Update feature completeness status
3. This file (CLAUDE.md) - Update recent improvements section

**Recommended reading order**:
1. This file (CLAUDE.md) - Overall project context
2. MISSING_FEATURES.md - Strategic planning and feature roadmap
3. docs/SPEC.md - Complete language specification

## Core Architecture

### Compilation Pipeline
1. **Lexical Analysis** (`src/tokens.py`) - Tokenizes A7 source code
2. **Syntax Analysis** (`src/parser.py`) - Recursive descent parser building ASTs
3. **AST Construction** (`src/ast_nodes.py`) - Comprehensive node types with factory functions
4. **Semantic Analysis** (`src/passes/`) - Three-pass analysis system
   - Name resolution, type checking, semantic validation
5. **Error Handling** (`src/errors.py`) - Rich formatting with specific error types
6. **Output Formatting** (`src/formatters/`) - Modular JSON and console formatters
7. **Code Generation** (`src/backends/`) - Backend interface (Zig target planned)
8. **Main Pipeline** (`src/compile.py`) - Orchestrates compilation (310 lines, refactored!)

### Key Implementation Details

**Tokenizer Features:**
- Single-token generics (`$T`, `$TYPE`) validated at tokenization
- Identifier/number length limits (100 chars)
- Hex escapes (`\x41`), nested comments
- All assignment operators including bitwise (&=, |=, ^=, <<=, >>=)

**Parser Architecture:**
- Recursive descent with precedence climbing
- Context-aware parsing (`_should_parse_struct_literal()`)
- Mixed parameter parsing (generics + regular)
- Span tracking for accurate error locations
- Successfully parses all A7 example files

**AST Design:**
- Enum-based with minimal inheritance
- Factory functions for consistent creation
- Complete operator mappings

## Development Commands

### Compilation & Analysis
```bash
# Standard compilation
uv run python main.py examples/001_hello.a7
uv run python main.py --json examples/014_generics.a7    # JSON output
./run.sh examples/021_control_flow.a7                    # Alternative

# Debugging modes
uv run python main.py --tokenize-only examples/006_if.a7  # Tokens only
uv run python main.py --parse-only examples/004_func.a7    # Tokens + AST
uv run python main.py --verbose examples/009_struct.a7     # Detailed output

# Test all examples
for file in examples/*.a7; do uv run python main.py "$file" || echo "FAILED: $file"; done
```

### Testing
```bash
# Run all tests
PYTHONPATH=. uv run pytest              # Run complete test suite
./test.sh                                # Alternative test runner

# Component tests by category
PYTHONPATH=. uv run pytest test/test_tokenizer.py                    # Tokenizer
PYTHONPATH=. uv run pytest test/test_parser_basic.py                 # Basic parsing
PYTHONPATH=. uv run pytest test/test_parser_examples.py              # All examples
PYTHONPATH=. uv run pytest test/test_parser_integration.py           # Integration tests
PYTHONPATH=. uv run pytest test/test_parser_creative_cases.py        # Creative patterns
PYTHONPATH=. uv run pytest test/test_parser_unicode_and_special.py   # Unicode & edge cases
PYTHONPATH=. uv run pytest test/test_parser_combinatorial.py         # Feature combinations
PYTHONPATH=. uv run pytest test/test_parser_advanced_edge_cases.py   # Advanced edge cases
PYTHONPATH=. uv run pytest test/test_parser_type_combinations.py     # Type system

# Pattern matching
PYTHONPATH=. uv run pytest -k "generic" -v       # All generic-related tests
PYTHONPATH=. uv run pytest -k "struct"           # All struct-related tests
PYTHONPATH=. uv run pytest -k "variadic"         # Variadic function tests
PYTHONPATH=. uv run pytest -k "not skip"         # Run only non-skipped tests

# Output modes
PYTHONPATH=. uv run pytest --tb=no -q   # Summary only
PYTHONPATH=. uv run pytest --tb=short   # Shorter tracebacks
PYTHONPATH=. uv run pytest -xvs         # Stop on first failure, verbose

# Debug specific test
PYTHONPATH=. uv run pytest test/test_parser_basic.py::TestBasicDeclarations::test_simple_function -xvs

# Quick validation
PYTHONPATH=. uv run pytest -k "not skip" --tb=no -q  # Fast check (non-skipped only)
```

### Environment Setup
```bash
uv sync                    # Install dependencies
uv add <package>          # Add dependency
uv tree                   # Show dependency tree
```

## Implementation Status

### ✅ PARSER 97% COMPLETE - Nearly All Language Features Implemented!

**Tokenizer/Lexer** (100% Complete):
- All A7 token types (keywords, operators, literals)
- All number formats (binary, octal, hex, decimal, floats, scientific notation)
- All escape sequences (basic, hex, unicode)
- Nested comments support
- Identifier and number length limits
- Tab detection and error reporting

**Parser** (97% Complete):
- All declaration types (functions, structs, enums, unions, type aliases)
- All control flow (if/else, while, for, for-in, match, break/continue)
- All expressions (literals, binary/unary ops, calls, indexing, field access)
- All type expressions (primitives, arrays, slices, pointers, function types, inline structs, generics)
- All memory management (new/del/defer)
- All import variants (basic, aliased, using, named items)
- Variadic functions (`fn(args: ..i32)`, `fn(args: ..)`)
- Type sets and generic constraints (`$T: @type_set(...)`)
- Builtin intrinsics (`@size_of(T)`, `@align_of(T)`, etc.)
- Generic struct literal instantiation (`Pair(i32, string){...}`)
- Cast expressions
- All assignment operators (including bitwise: `&=`, `|=`, `^=`, `<<=`, `>>=`)
- Pattern matching (literals, ranges, wildcards, enum variants)
- Complex nested expressions

**Deferred** (3% - low priority):
- ⏸️ Labeled loops (syntax ambiguity: `label: type` vs `variable: type`)

**AST Generation** (100% Complete):
- Complete AST for entire language
- Source span tracking for all nodes
- Factory functions for consistent node creation
- Error system with Rich formatting
- JSON output mode

### 🚧 In Development (Next Phases)
- **Semantic Analysis**: Type checking, name resolution, symbol tables
- **Code Generation**: Zig backend implementation
- **Optimization**: Code optimization passes
- **Standard Library**: Array programming primitives

### Next Steps: Semantic Analysis & Code Generation

**Semantic Analysis Phase** (Not yet started):
1. **Symbol Tables** - Scope management, name resolution, import tracking
2. **Type System** - Type inference, checking, generic monomorphization
3. **Semantic Validation** - Return types, break/continue context, memory safety
4. **Additional Checks** - Unreachable code, unused variables, type compatibility

**Code Generation Phase** (Not yet started):
1. **Zig Backend** - AST → Zig translation, memory management mapping
2. **Optimization** - Dead code elimination, constant folding, inlining
3. **Future Backends** - C, native machine code

### Notes
- ✅ All A7 example files parse successfully (100% real-world coverage)
- ✅ 465/481 tests passing (96.7% success rate)
- 📝 "Module qualified access" and "Import alias tracking" are semantic analysis concerns, not parser issues
- ⏸️ Labeled loops deferred - requires language design decision on syntax disambiguation
- 🎯 Parser phase complete - focus now shifts to semantic analysis and code generation

## A7 Language Quick Reference

### Critical Syntax Differences from C-like Languages

**Operators**:
- Use `and`, `or`, `not` keywords - NOT `&&`, `||`, `!`
- Compound assignments supported: `+=`, `-=`, `*=`, `/=`, `&=`, `|=`, `^=`, `<<=`, `>>=`

**Nil Semantics**:
- `nil` ONLY valid for reference types (`ref T`)
- Arrays, structs, primitives CANNOT be `nil`
- Uninitialized arrays auto-zero: `arr: [5]i32` → `[0, 0, 0, 0, 0]`

**Pointer Syntax** (property-based, not operators):
- `variable.adr` for address-of (NOT `&variable`)
- `ptr.val` for dereference (NOT `*ptr`)

**Generics**:
- `$T` declares a generic parameter
- `T` references a declared parameter (no `$` in usage)

### Declarations
```a7
// Constants (immutable)
PI :: 3.14159

// Variables (mutable) with type inference
count := 0

// Explicit type annotation
x: i32 = 42
```

### Array Types
```a7
[3][4]i32       // 3x4 matrix
[][]f64         // Slice of slices
[][][][][]i32   // 5-dimensional array

// NOT: [[3]i32] or [[[i32]]] - invalid syntax
```

### Pointer Syntax (Property-Based)
```a7
ptr := variable.adr      // Address-of (&variable in C)
value := ptr.val         // Dereference (*ptr in C)
ptr.val = 42            // Assignment through pointer
ppp.val.val.val         // Multiple indirection
```

### Generics
```a7
// $T declares generic parameter, T uses it
swap :: fn($T, a: ref T, b: ref T) {
    temp := a.val
    a.val = b.val
    b.val = temp
}

// Constraints with predefined type set
abs :: fn($T: Numeric, x: T) T {
    ret if x < 0 { -x } else { x }
}

// Constraints with inline type set
process :: fn($T: @type_set(i32, i64), value: T) T {
    ret value * 2
}
```

### Control Flow
```a7
// For loops
for i := 0; i < 10; i := i + 1 { }  // C-style
for x in array { }                   // Range-based
for i, x in array { }                // Indexed

// Match statement
match value {
    case 1: print("one")
    case 2, 3: print("two or three")
    else: print("other")
}
```

## Parser Development Workflow

When implementing new features:

1. **Identify construct** - Use failing example to pinpoint syntax
2. **Check tokenization** - `--tokenize-only` to verify tokens
3. **Add parser method** - Follow patterns in `src/parser.py`
4. **Update AST nodes** - Add to `src/ast_nodes.py` if needed
5. **Test incrementally** - Use `--parse-only` to debug
6. **Add tests** - Cover edge cases in test files

**Key Patterns:**
- `parse_*_statement()` for control flow
- `parse_*_expression()` for values
- `parse_*_decl()` for top-level declarations
- `create_span_from_token()` for error locations
- Precedence climbing for binary operators

**Debugging Tips:**
```bash
# When parser fails on an example file:
uv run python main.py --tokenize-only examples/XXX.a7  # Check tokens are correct
uv run python main.py --parse-only examples/XXX.a7     # See AST output
uv run python main.py --verbose examples/XXX.a7        # Detailed compilation info

# When a test fails:
PYTHONPATH=. uv run pytest path/to/test.py::TestClass::test_method -xvs  # Stop and show details
PYTHONPATH=. uv run pytest path/to/test.py -k "keyword" -v               # Run matching tests
```

## Test Coverage Highlights

The parser handles extreme cases successfully:
- ✅ Deeply nested parentheses
- ✅ Deeply nested blocks
- ✅ Long function call chains
- ✅ Unicode in strings (emojis, math symbols, CJK)
- ✅ Very long string literals
- ✅ Large numbers of declarations in single file
- ✅ Complex multi-operand expressions

## Common Issues & Troubleshooting

### Parser Fails on Valid-Looking Code
1. Check for `&&`/`||` instead of `and`/`or` keywords
2. Verify `nil` only used with reference types (`ref T`)
3. Ensure pointers use `.adr`/`.val` not `&`/`*`
4. Check array initialization (uninitialized arrays auto-zero, don't use `nil`)

### Test Failures
1. Run `PYTHONPATH=. uv run pytest -xvs` to see full error details
2. Check if example files need updating with `uv run python main.py --parse-only examples/XXX.a7`
3. Verify tokenization first with `--tokenize-only` flag
4. Look for changes in CHANGELOG.md that might affect tests

### Import/Module Issues
Remember: Module qualified access (`io.println`) and import aliases are **semantic analysis** concerns, not parser issues. The parser correctly handles the syntax - semantic validation comes later.

## Specialized Agents

Use `Task` tool with `subagent_type=compiler-test-engineer` for:
- Adding test coverage for new features
- Testing edge cases in tokenizer/parser
- Validating error messages
- Ensuring examples continue working

## Project Files Summary

- **Entry point**: `main.py` - CLI with multiple analysis modes
- **Core pipeline**: `src/compile.py` - Orchestrates compilation
- **Documentation**:
  - `docs/SPEC.md` - Complete A7 language specification
  - `MISSING_FEATURES.md` - Comprehensive feature gap analysis
  - `CHANGELOG.md` - All notable changes and version history
  - `examples/README.md` - Catalog of all example programs
- **Examples**: A7 programs organized into:
  - Basic features: Hello world, functions, control flow, structs, etc.
  - Advanced features: Generics, enums, unions, memory management, error handling
  - Real-world demos: Function pointers, linked lists, binary trees, state machines, sorting, calculators, games, string utils, matrix ops
  - See `examples/README.md` for complete catalog
- **Configuration**: `pyproject.toml`, `.claude/settings.json`
- **Dependencies**: Python 3.13+, pytest, rich, uv
- **Design Philosophy**: Data-oriented approach throughout