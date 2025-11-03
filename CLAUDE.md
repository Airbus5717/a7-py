# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A7 programming language compiler implemented in Python. A7 is a statically-typed, procedural language with array programming capabilities, generics, and manual memory management. The compiler targets Zig as the output language.

## Project Status & TODO List

**Current Test Results**: 411/411 passing (100% test success!) 🎉
- ✅ **Tokenizer**: 100% functional (all issues resolved)
- ✅ **Parser**: 100% tests passing (Track 1 complete!)
- ✅ **Function Types**: Fully implemented
- ✅ **Inline Struct Types**: Fully implemented
- 📊 **Feature Completeness**: ~72% of spec features implemented

**Recent Improvements** (2025-11-03):
- ✅ Implemented inline/anonymous struct types (`struct { id: i32, data: string }`)
- ✅ Implemented function type parsing (`fn(i32) i32`, function pointers)
- ✅ Added 48 comprehensive test cases (type combinations + edge cases)
- ✅ Parser completeness increased from 65% to 72%
- ✅ Type system completeness increased from 67% to 89%

**Key Documentation**:
- **`CHANGELOG.md`** - Track all changes here! Update for every feature/fix
- **`TODOLIST.md`** - Implementation roadmap with Track 1 ✅ COMPLETE
  - Track 1: Parser fixes → 100% tests passing ✅
  - Track 2: Strategic features (P0/P1) for production readiness
  - Clear documentation of completed vs remaining work
- **`MISSING_FEATURES.md`** - Comprehensive feature gap analysis
  - Feature completeness by category (types: 89%, imports: 25%, builtins: 0%)
  - Priority ranking (P0 critical → P3 future)
  - 4-sprint implementation roadmap
  - Dependency graphs and risk assessment

**IMPORTANT**: When adding new features or fixing bugs, always update:
1. `CHANGELOG.md` - Add entry under [Unreleased] section
2. `TODOLIST.md` - Mark completed items, update status
3. `MISSING_FEATURES.md` - Update feature completeness percentages
4. This file (CLAUDE.md) - Update test counts and recent improvements

**Recommended reading order**:
1. This file (CLAUDE.md) - Overall project context
2. TODOLIST.md - Track 1 complete, Track 2 next steps
3. MISSING_FEATURES.md - Long-term strategic planning

## Core Architecture

### Compilation Pipeline
1. **Lexical Analysis** (`src/tokens.py`, 913 lines) - Tokenizes A7 source code
2. **Syntax Analysis** (`src/parser.py`, ~1780 lines) - Recursive descent parser building ASTs
3. **AST Construction** (`src/ast_nodes.py`, 573 lines) - 80+ node types with factory functions
4. **Error Handling** (`src/errors.py`, 516 lines) - Rich formatting with 18+ error types
5. **Code Generation** (`src/backends/`) - Backend interface (Zig target planned)
6. **Main Pipeline** (`src/compile.py`, 639 lines) - Orchestrates compilation

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
- Successfully parses all 36 A7 example files

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

### Testing (353 total tests, ~7200 lines)
```bash
# Run all tests
PYTHONPATH=. uv run pytest              # 352 passing, 1 skipped (100% active!)
./test.sh                                # Alternative

# Component tests by file
PYTHONPATH=. uv run pytest test/test_tokenizer.py           # Tokenizer only
PYTHONPATH=. uv run pytest test/test_parser_examples.py     # All 36 examples (100% pass)
PYTHONPATH=. uv run pytest test/test_parser_integration.py  # Integration tests
PYTHONPATH=. uv run pytest test/test_parser_extreme_edge_cases.py  # Edge cases (5 failures)

# Pattern matching
PYTHONPATH=. uv run pytest -k "generic" -v
PYTHONPATH=. uv run pytest -k "struct"
PYTHONPATH=. uv run pytest -k "not extreme_edge" # Skip failing edge cases

# Output modes
PYTHONPATH=. uv run pytest --tb=no -q   # Summary only
PYTHONPATH=. uv run pytest --tb=short   # Shorter tracebacks
PYTHONPATH=. uv run pytest -xvs         # Stop on first failure, verbose

# Debug specific test
PYTHONPATH=. uv run pytest test/test_parser_extreme_edge_cases.py::TestDeepNesting::test_deeply_nested_parentheses -xvs

# Quick validation (skip edge cases)
PYTHONPATH=. uv run pytest -k "not extreme_edge" --tb=no -q
```

### Environment Setup
```bash
uv sync                    # Install dependencies
uv add <package>          # Add dependency
uv tree                   # Show dependency tree
```

## Implementation Status

### ✅ Complete (All 36 examples parse successfully + 100% test success)
- Tokenizer with all A7 token types
- Parser for all major language constructs
- AST generation for complete grammar
- Error system with Rich formatting
- JSON output mode
- Generic types with constraints and instantiation (`List($T)`, `Map(K, V)`)
- All declaration types (functions, structs, enums, unions)
- All control flow (if/else, while, for, match)
- Memory management (new/del/defer)
- Import statements with named imports
- Cast expressions
- Assignment operators (all variants)
- Uninitialized variable declarations (`arr: [5]i32`)
- Standalone block statements (`{ x := 1 }`)
- Complex type expressions (arrays of pointers, multi-dimensional arrays)

### 🚧 In Development
- Code generation to Zig (backend architecture exists)
- Type checking and semantic analysis
- Optimization passes

### Known Limitations (Strategic Features - See MISSING_FEATURES.md)
**All tests passing!** Remaining work is adding new language features, not fixing bugs.

**Not Yet Implemented** (documented in skipped test):
1. **Function type parsing** - `callback: fn(i32) i32` (TODO at parser.py:547)
2. **Inline struct types** - `data: struct { id: u64 }` in type position
3. **Module qualified access** - Semantic distinction between `io.println()` and `obj.field`
4. **Import alias tracking** - Symbol table support for `io :: import "std/io"`

**Note**: All 36 A7 example files parse successfully (100% real-world coverage). All 411 active tests pass.

## A7 Language Quick Reference

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
fn add(a: $T, b: $T) $T {
    ret a + b
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
- ✅ 100-level deep parentheses
- ✅ 50-level deep nested blocks
- ✅ 50-level function call chains
- ✅ Unicode in strings (emojis, math symbols, CJK)
- ✅ 10,000 character string literals
- ✅ 1000 declarations in single file
- ✅ 100-operand expressions

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
  - `TODOLIST.md` - 5 failing test fixes (edge cases)
  - `MISSING_FEATURES.md` - Comprehensive feature gap analysis (~60% complete)
- **Examples**: 36 files including feature demos (000-029) and practical programs (030-035)
- **Configuration**: `pyproject.toml`, `.claude/settings.json`
- **Dependencies**: Python 3.13+, pytest, rich, uv