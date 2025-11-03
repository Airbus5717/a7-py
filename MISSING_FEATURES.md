# A7 Parser Missing Features Analysis

**Last Updated**: 2025-11-03 (Function types implemented!)
**Parser Completeness**: ~68% of spec features
**Test Success Rate**: 353/354 (100% active tests, 1 skipped for unimplemented features)

---

## Executive Summary

The A7 parser has **excellent foundational implementation** with 100% success on all tests and all 22 example files. Track 1 (tactical parser fixes) is complete and function type parsing is now fully implemented. This document identifies remaining strategic features to implement for production readiness.

**Recent Improvements**:
- ✅ **Function type parsing implemented** (`fn(i32) i32`, `fn() void`, arrays of function pointers)
- ✅ Generic type instantiation now works (`List($T)`, `Map(K, V)`)
- ✅ Uninitialized variable declarations supported
- ✅ All parser edge cases resolved

---

## Feature Completeness by Category

| Category | Implemented | Missing/Partial | Percentage |
|----------|------------|-----------------|------------|
| **Declarations** | 6/7 | 1 (type sets) | 86% |
| **Control Flow** | 7/7 | 0 | **100%** ✅ |
| **Expressions** | 13/13 | 0 | **100%** ✅ |
| **Types** | 7/9 | 2 (type sets, anonymous structs) | **78%** ⬆️ |
| **Memory Management** | 4/4 | 0 | **100%** ✅ |
| **Imports** | 1/4 | 3 (aliases, named, using) | **25%** ⚠️ |
| **Generics** | 3/5 | 2 (type sets, struct literal instantiation) | **60%** ⬆️ |
| **Builtins** | 0/5 | 5 (all @ intrinsics) | **0%** ⚠️ |
| **Array Programming** | 0/10 | 10 (entire section 9) | 0% |

---

## Critical Missing Features (P0)

### 1. Module Qualified Access - **CRITICAL**
```a7
io.println("hello")  // Used in 18/22 examples!
```
**Status**: Parsed as field access, not module access
**Impact**: Affects 81% of example files
**Fix needed**: Distinguish module.function from object.field
**Severity**: **CRITICAL** - breaks semantic analysis

### 2. Named Import Aliases - **CRITICAL**
```a7
io :: import "std/io"
```
**Status**: Parses but alias not properly tracked
**Impact**: Affects 18/22 examples
**Fix needed**: Store and use alias binding in symbol table
**Severity**: **CRITICAL** - needed for proper name resolution

### 3. ✅ Function Type Parsing - **COMPLETE**
```a7
callback: fn(i32, i32) i32
handlers: [10]fn() void
```
**Status**: ✅ Fully implemented as of 2025-11-03
**Implementation**: 55 lines across parser.py and ast_nodes.py
**Tests**: 353/354 passing (4 new tests added)
**Impact**: Function pointers and higher-order functions now fully supported

---

## High Priority Missing Features (P1)

### 4. Variadic Functions
```a7
sum :: fn(values: ..i32) i32
printf :: fn(format: string, args: ..)
```
**Status**: AST has `is_variadic` flag but no parsing
**Spec**: Section 6.5
**Used in**: printf/scanf patterns

### 5. Type Sets (@set)
```a7
Numeric :: @set(i8, i16, i32, i64, f32, f64)
fn($T: Numeric, x: T) T { }
```
**Status**: AST has TYPE_SET node but no parsing
**Spec**: Section 7.3
**Needed for**: Generic constraints

### 6. Generic Struct Literal Instantiation
```a7
p := Pair(i32, string){42, "answer"}  // Type instantiation in literal
```
**Status**: Partially implemented
**Note**: Generic type instantiation in **type expressions** now works: `list: List($T) = nil`
**Missing**: Combining type parameters with struct literal: `Pair(i32, string){...}`
**Spec**: Section 7.2
**Example**: 014_generics.a7:48

### 7. Labeled Loops
```a7
outer: for i := 0; i < 10; i += 1 {
    break outer
}
```
**Status**: AST has `label` field but no parsing
**Spec**: Section 5.4

### 8. Named Item Imports
```a7
import "vector" { Vec3, dot }
```
**Status**: Not implemented
**Spec**: Section 10.2

---

## Medium Priority Features (P2)

### 9. Builtin Intrinsics (@ functions)
```a7
@size_of(T)      // Size intrinsic
@align_of(T)     // Alignment intrinsic
@type_id(T)      // Type identifier
@unreachable()   // Unreachable marker
```
**Status**: Not implemented (0/5 intrinsics)
**Spec**: Section 10.1
**Token**: BUILTIN_ID exists but no parsing

### 10. Anonymous Struct Types
```a7
sincos :: fn(angle: f64) struct { sin: f64, cos: f64 }
```
**Status**: Not implemented
**Spec**: Section 6.1
**Use case**: Return multiple values

### 11. Using Imports
```a7
using import "vector"
```
**Status**: AST has `is_using` field but no parsing
**Spec**: Section 10.2

### 12. Generic Type Constraints (Full)
```a7
fn($T: Numeric + Comparable, x: T) T
```
**Status**: Partial - basic constraints parse but not full syntax
**Spec**: Section 7.3

---

## Low Priority / Future Features (P3)

### 13. Array Programming Features (Section 9)

**Status**: Completely missing (0/10 features)
**Impact**: LOW (no examples use these)
**Note**: Likely standard library, not parser features

Missing features:
- Tensor types (9.1)
- Broadcasting (9.2)
- Tensor manipulation (9.3)
- Reduction operations (9.4)
- Linear algebra (9.5)
- AI primitives (9.6)
- Advanced indexing (9.8)

### 14. String Escape Sequences (Comprehensive)
**Status**: Basic escapes work, comprehensive parsing needed
**TODO**: ast_nodes.py:529
**Spec**: Section 2.6 lists 12 escape sequences

---

## Explicit TODO Comments in Code

### src/parser.py:547
```python
# TODO: Implement function type parsing
```
**Priority**: HIGH
**Category**: Type System

### src/ast_nodes.py:529
```python
# TODO: Proper string escape sequence parsing
```
**Priority**: MEDIUM
**Category**: Literals

---

## Failing Edge Case Tests (5 Tests)

### From test_parser_extreme_edge_cases.py:

1. **test_struct_literal_vs_block**
   - Issue: Ambiguity between `Type{...}` and blocks
   - Status: Heuristic fails in edge cases

2. **test_generic_vs_comparison**
   - Issue: Nested function declarations inside functions
   - Code: `swap :: fn(a: ref $T, b: ref $T) {}`

3. **test_array_type_vs_array_literal**
   - Issue: Uninitialized variable declarations
   - Code: `arr: [5]i32` (no `=`)

4. **test_incomplete_statements**
   - Issue: Parser doesn't reject incomplete syntax
   - Code: `x := }`, `if }`, `for }`

5. **test_complex_type_expressions**
   - Issue: Function types and inline struct types
   - Code: `callback: fn(i32) i32`, `data: struct { ... }`

**See TODOLIST.md for detailed fix instructions**

---

## Fully Implemented Features ✅

### Control Flow
- ✅ If/else statements and expressions
- ✅ While loops
- ✅ C-style for loops (`for i := 0; i < 10; i += 1`)
- ✅ Range-based for loops (`for x in arr`, `for i, x in arr`)
- ✅ Match statements with patterns (range, enum, multiple values)
- ✅ Break/continue

### Memory Management
- ✅ New expression (`new T`, `new [N]T`)
- ✅ Del statement (`del ptr`)
- ✅ Defer statement (`defer del ptr`)
- ✅ Pointer operations (`.adr`, `.val`)

### Expressions
- ✅ Binary operators (all precedence levels)
- ✅ Unary operators
- ✅ Array literals (`[1, 2, 3]`)
- ✅ Struct literals (named and positional)
- ✅ Cast expressions (`cast(T, x)`)
- ✅ If expressions
- ✅ Function calls
- ✅ Array indexing
- ✅ Field access
- ✅ Property access (`.adr`, `.val`, `.len`)

### Declarations
- ✅ Function declarations
- ✅ Struct declarations
- ✅ Enum declarations
- ✅ Union declarations
- ✅ Constant declarations
- ✅ Variable declarations

### Types
- ✅ Primitive types (i8, i16, i32, i64, u8, u16, u32, u64, f32, f64, bool, char, string)
- ✅ Array types (`[N]T`)
- ✅ Slice types (`[]T`)
- ✅ Pointer types (`ref T`)
- ✅ Generic type parameters (`$T`)
- ✅ Generic type instantiation (`List($T)`, `Map(K, V)`)
- ✅ Function types (`fn(i32, i32) i32`, `fn() void`, `[10]fn() void`) - **NEW!**
- ✅ Multi-dimensional arrays (`[M][N]T`)
- ✅ Complex combinations (`[N]ref T`, `ref [N]T`, `ref ref T`)

---

## Implementation Roadmap

### Sprint 1: Critical Fixes (1-2 weeks)
**Goal**: Fix import system and function types

1. Implement module qualified access semantic handling
2. Fix named import alias tracking
3. Complete function type parsing (remove TODO)
4. Add variadic parameter parsing

**Expected**: Proper name resolution, function pointers work

### Sprint 2: Type System (2-3 weeks)
**Goal**: Complete advanced type features

5. Implement type sets (@set)
6. Add generic struct instantiation syntax
7. Implement anonymous struct types
8. Complete generic constraint system

**Expected**: Full generic programming support

### Sprint 3: Language Features (1-2 weeks)
**Goal**: Complete missing language constructs

9. Add labeled loop support
10. Implement named/using import variants
11. Implement builtin intrinsics (@size_of, @align_of, etc.)
12. Improve string escape sequence handling

**Expected**: Feature parity with spec

### Sprint 4: Polish & Testing (1 week)
**Goal**: Fix all edge cases

13. Fix 5 failing edge case tests
14. Improve error messages
15. Add missing test coverage
16. Performance optimization

**Expected**: 352/352 tests passing (100%)

### Future: Backend Implementation
- Semantic analysis and type checking
- Code generation to Zig
- Optimization passes
- Array programming standard library

---

## Dependency Graph

```
Critical Path:
1. Module qualified access → Name resolution → Semantic analysis
2. Import aliases → Symbol tables → Type checking
3. Function types → Higher-order functions → Advanced patterns

Independent:
- Labeled loops (standalone feature)
- Builtin intrinsics (standalone)
- String escapes (standalone)

Depends on Type System:
- Type sets → Generic constraints
- Anonymous structs → Multiple returns
- Generic instantiation → Template system
```

---

## Risk Assessment

### High Risk
- **Module qualified access**: Affects 81% of examples, critical for real use
- **Import aliases**: Fundamental to module system

### Medium Risk
- **Function types**: Important but workarounds exist
- **Variadic functions**: Common pattern but not critical

### Low Risk
- **Labeled loops**: Niche feature
- **Array programming**: Future/optional features
- **Edge case fixes**: Don't affect normal usage

---

## Testing Coverage

### Current Status
- **Examples**: 22/22 tokenize correctly, 22/22 parse successfully
- **Unit tests**: 347/352 passing (98.6%)
- **Edge cases**: 5/11 fixed (from original 11 failures)

### Gaps
- No tests for missing features (function types, type sets, etc.)
- Limited stress testing for complex type expressions
- No integration tests for import system

### Needed
- Add tests for each missing feature as implemented
- Expand edge case coverage
- Add semantic analysis tests (separate from parser tests)

---

## Comparison with Other Languages

### A7 vs Zig Similarities
- Similar type system structure
- Both have explicit memory management
- Both compile-time known sizes

### A7 Unique Features
- Property-based pointer syntax (`.adr`, `.val`)
- Single-token generics (`$T`)
- Array programming focus
- Simpler import system

### Implementation Status vs Spec
- **Zig parser**: ~95% feature complete
- **A7 parser**: ~60% feature complete
- **Gap**: Import system, type system, builtins

---

## Recommendations

### Immediate Actions
1. **Fix module access** - Critical blocker for real programs
2. **Fix import aliases** - Foundation of module system
3. **Complete function types** - Explicit TODO, high value

### Next Steps
4. **Add type sets** - Generic constraints essential
5. **Add variadic functions** - Common pattern in many languages
6. **Implement builtins** - Standard library needs these

### Long Term
7. **Array programming** - Differentiation feature, but low priority
8. **Semantic analysis** - Separate phase, not parser work
9. **Code generation** - Backend implementation

---

## Related Files

- `TODOLIST.md` - Detailed fixes for 5 failing tests
- `CLAUDE.md` - Project overview and development guide
- `docs/SPEC.md` - Complete A7 language specification
- `src/parser.py` - Main parser implementation (1705 lines)
- `src/ast_nodes.py` - AST node definitions (573 lines)
- `examples/*.a7` - 22 working example programs

---

**Summary**: The A7 parser has excellent coverage of core features but needs completion of import system (25% done), type system (56% done), and builtin functions (0% done) to reach production readiness. The critical path is: module access → import aliases → function types → type sets.
