# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A7 programming language compiler in Python. A7 is a statically-typed, procedural language with array programming capabilities, generics, and manual memory management. The compiler targets Zig as output.

**Current state**: Full compilation pipeline working. 786 tests passing. 18/36 examples compile end-to-end (18 blocked by semantic analysis gaps). All AST traversals are iterative — no recursion anywhere in the pipeline.

**Key docs**: `docs/SPEC.md` (language spec), `MISSING_FEATURES.md` (feature status & roadmap), `CHANGELOG.md` (change log).

**When adding features or fixing bugs**, update: `CHANGELOG.md`, `MISSING_FEATURES.md`, and this file.

## Development Commands

```bash
# Setup
uv sync

# Run compiler
uv run python main.py examples/001_hello.a7
uv run python main.py --mode tokens examples/006_if.a7      # Tokens only
uv run python main.py --mode ast examples/004_func.a7       # Tokens + AST
uv run python main.py --format json examples/014_generics.a7  # JSON output
uv run python main.py --verbose examples/009_struct.a7      # Detailed output
uv run python main.py examples/001_hello.a7 --mode compile --doc-out auto # Generate .md report
uv run python main.py examples/001_hello.a7 --mode compile --doc-out out.md  # Custom doc path

# Exit codes
# 0 success, 2 usage, 3 io, 4 tokenize, 5 parse, 6 semantic, 7 codegen, 8 internal

# Run all tests
PYTHONPATH=. uv run pytest

# Run specific tests
PYTHONPATH=. uv run pytest test/test_tokenizer.py
PYTHONPATH=. uv run pytest test/test_parser_basic.py::TestBasicDeclarations::test_simple_function -xvs
PYTHONPATH=. uv run pytest -k "generic" -v
PYTHONPATH=. uv run pytest --tb=no -q                       # Summary only
```

## Architecture

### Compilation Pipeline (`src/compile.py`)

`A7Compiler.compile_file()` orchestrates this sequential pipeline:

1. **Tokenizer** (`src/tokens.py`) — Source → token list. Single-token generics (`$T`), nested comments, all number formats.
2. **Parser** (`src/parser.py`) — Tokens → AST. Recursive descent with precedence climbing for expressions.
3. **AST** (`src/ast_nodes.py`) — `NodeKind` enum + `ASTNode` dataclass with preprocessor annotations (`is_mutable`, `is_used`, `emit_name`, `resolved_type`, `hoisted`, `stdlib_canonical`).
4. **Semantic Analysis** (`src/passes/`) — Three sequential passes, each gated on previous pass succeeding:
   - **Name Resolution** (`name_resolution.py`) — Builds `SymbolTable` with hierarchical `Scope`s
   - **Type Checking** (`type_checker.py`) — Infers/checks types, produces `node_types` map
   - **Semantic Validation** (`semantic_validator.py`) — Control flow, memory management, misc checks
5. **AST Preprocessing** (`src/ast_preprocessor.py`) — 9 sub-passes: `.adr`/`.val` lowering, stdlib resolution, struct init normalization, mutation analysis, usage analysis, type inference, shadowing resolution, function hoisting, constant folding.
6. **Code Generation** (`src/backends/zig.py`) — AST → Zig source. Reads preprocessor annotations for emit_name, hoisted, is_used, resolved_type.

### Supporting Modules

- `src/errors.py` — Error types with Rich formatting and `SourceSpan`. Error enums: `TokenizerErrorType`, `SemanticErrorType`, `TypeErrorType`.
- `src/types.py` — Type system: `Type` base class with subclasses (`PrimitiveType`, `ArrayType`, `PointerType`, `FunctionType`, etc.). Immutable/hashable.
- `src/symbol_table.py` — `Symbol` (name + kind + type) and `Scope` (nested symbol lookup).
- `src/semantic_context.py` — Analysis state: `FunctionContext`, `LoopContext`, `DeferContext`.
- `src/generics.py` — Generic type infrastructure and monomorphization.
- `src/module_resolver.py` — Module/import resolution.
- `src/stdlib/` — Standard library registry with backend-specific mappings (io, math, mem, string).
- `src/formatters/` — `JSONFormatter`, `ConsoleFormatter`, and `MarkdownFormatter` for output.

### Key Design: No Recursion

All AST traversals use explicit stacks. The full pipeline works with `sys.setrecursionlimit(100)`. This applies to: preprocessor, all 3 semantic passes, Zig backend, generics, and formatters.

### Zig Codegen Key Mappings

- AST node attributes: `node.operator` (not `op`), `node.literal_value` (not `value`), `node.parameter_types` (not `param_types`)
- BinaryOp enums: `SUB`, `MUL`, `DIV`, `MOD`, `EQ`, `NE`, `LT`, `LE`, `GT`, `GE`, `BIT_AND`, `BIT_OR`, `BIT_XOR`, `BIT_SHL`, `BIT_SHR`
- UnaryOp enums: `NEG`, `NOT`, `BIT_NOT`

## A7 Syntax Gotchas

These are the most common mistakes when writing A7 code (e.g., in tests):

- **Logical operators**: `and`, `or`, `not` — NOT `&&`, `||`, `!`
- **Nil**: only valid for `ref T` types — arrays, structs, primitives cannot be `nil`
- **Pointers**: `x.adr` (address-of), `p.val` (dereference) — NOT `&x`, `*p`
- **Generics**: `$T` declares a parameter, bare `T` references it in usage
- **Constants**: `PI :: 3.14` (double colon); **Variables**: `x := 0` (colon-equals)
- **Explicit type**: `x: i32 = 42`
- **Arrays**: `[3][4]i32` (3×4 matrix), `[]i32` (slice) — NOT `[[3]i32]`
- **Uninitialized arrays auto-zero**, don't assign `nil` to them

## Specialized Agents

Use `Task` tool with `subagent_type=compiler-test-engineer` for adding test coverage, testing edge cases, and validating error messages.

## Deferred Features

- **Labeled loops** — deferred due to syntax ambiguity (`label: type` vs `variable: type`). AST has `label` field reserved.
