# A7 Semantic Analysis Implementation Phases

Implementation roadmap for completing the semantic analysis system based on error analysis of all 36 example files.

**Current Status**: 98/228 semantic tests passing (43%)
**Error Count**: ~3,300 errors across 31/36 example files

---

## Phase 1: Module System & Symbol Resolution 🎯
**Priority**: P0 - Critical
**Impact**: Will fix ~60% of all errors (~2,000 errors)
**Target**: Examples 001-007 compile cleanly

### Goals
- Implement standard library module system
- Fix symbol table to properly track variables and parameters
- Support module-qualified access (`io.println`)

### Key Deliverables
1. **Module Resolution System**
   - Built-in `io` module with `println`, `print`, `read_line` functions
   - Module symbol table infrastructure
   - Module-qualified name lookup (`module.function`)
   - Import statement processing

2. **Symbol Table Fixes**
   - Function parameters registered in scope
   - Local variable declarations tracked
   - Loop variable declarations (`for i := 0; ...`, `for i in arr`)
   - Proper scope enter/exit semantics

3. **Testing**
   - All basic examples (001-007) compile without errors
   - Symbol resolution tests pass
   - Module access tests pass

### Success Metrics
- ✅ `io.println` resolves correctly in all examples
- ✅ Function parameters accessible in function body
- ✅ Loop variables (`i`, `j`) found in scope
- ✅ Local variables tracked across scopes
- ✅ Error count reduced by ~2,000 (60% reduction)

### Estimated Examples Fixed
- 001_hello.a7 (3 errors → 0)
- 002_var.a7 (20 errors → ~2)
- 004_func.a7 (28 errors → ~5)
- 005_for_loop.a7 (80 errors → ~10)
- 006_if.a7 (59 errors → ~5)
- 007_while.a7 (58 errors → ~5)

---

## Phase 2: Type Inference & Propagation 🔍
**Priority**: P0 - Critical
**Impact**: Will fix ~25% of remaining errors (~650 errors)
**Target**: Examples 008-015 compile cleanly

### Goals
- Implement type inference for variable declarations
- Propagate types through assignments and expressions
- Handle generic type instantiation

### Key Deliverables
1. **Type Inference Engine**
   - Infer types from literal initializers (`x := 42` → `i32`)
   - Infer from function returns (`result := add(1, 2)` → `i32`)
   - Infer from expressions (`sum := a + b` → infer from `a`, `b` types)
   - Infer array element types from initialization

2. **Type Propagation**
   - Assignment type flow (`x := 1; y := x` → both `i32`)
   - Compound assignment targets (`count += 5` needs `count` type)
   - Function call argument inference
   - Return type inference from body

3. **Generic Instantiation**
   - Generic function calls (`swap(x, y)` → instantiate `$T`)
   - Generic struct initialization (`List(i32){...}`)
   - Type constraint checking

### Success Metrics
- ✅ `x := 42` infers `i32` type
- ✅ `count += 5` works when `count` is inferred
- ✅ Array operations work on inferred types
- ✅ Generic functions instantiate correctly
- ✅ Error count reduced by ~650 (25% of remaining)

### Estimated Examples Fixed
- 009_struct.a7 (19 errors → ~3)
- 011_memory.a7 (266 errors → ~50)
- 012_arrays.a7 (178 errors → ~20)
- 013_pointers.a7 (223 errors → ~30)
- 014_generics.a7 (46 errors → ~5)

---

## Phase 3: Return Types & Control Flow 🔄
**Priority**: P1 - High
**Impact**: Will fix ~15% of remaining errors (~240 errors)
**Target**: Examples 016-022 compile cleanly

### Goals
- Fix return type checking
- Improve control flow analysis
- Handle early returns and multiple paths

### Key Deliverables
1. **Return Type Evaluation**
   - Compute return expression type before comparison
   - Handle void returns (no expression)
   - Verify return type matches function signature
   - Track whether all paths return

2. **Control Flow Analysis**
   - Track return paths through if/else
   - Handle early returns
   - Validate unreachable code detection
   - Match statement exhaustiveness

3. **Expression Type Evaluation**
   - Binary operation result types
   - Unary operation result types
   - Ternary expression types (`if x then a else b`)
   - Type coercion rules

### Success Metrics
- ✅ `ret x + y` correctly validates against function return type
- ✅ Void functions don't require return value
- ✅ Non-void functions warn if missing return
- ✅ Control flow correctly tracks return paths
- ✅ Error count reduced by ~240 (15% of remaining)

### Estimated Examples Fixed
- 004_func.a7 (remaining return errors)
- 021_control_flow.a7 (13 errors → 0)
- 022_function_pointers.a7 (46 errors → ~10)

---

## Phase 4: Enum & Union Support 🏷️
**Priority**: P1 - High
**Impact**: Will fix ~5% of remaining errors (~80 errors)
**Target**: Examples with enums/unions compile cleanly

### Goals
- Support enum variant access
- Support union tag access
- Distinguish from struct field access

### Key Deliverables
1. **Enum Variant Resolution**
   - Resolve `Color.Red` as enum variant, not struct field
   - Validate variant exists in enum definition
   - Type enum literal as the enum type
   - Pattern matching on enum variants

2. **Union Tag Access**
   - Access union tag field
   - Type check union access patterns
   - Validate tag-based access safety

3. **Pattern Matching**
   - Match on enum variants
   - Extract variant data
   - Exhaustiveness checking

### Success Metrics
- ✅ `Color.Red` resolves as enum variant
- ✅ Enum pattern matching works
- ✅ Union tag access validated
- ✅ Error count reduced by ~80

### Estimated Examples Fixed
- 010_enum.a7 (8 errors → 0)
- 016_unions.a7 (3 errors → 0)

---

## Phase 5: Pointer & Reference Operations 👉
**Priority**: P2 - Medium
**Impact**: Will fix ~10% of remaining errors (~160 errors)
**Target**: Memory management examples work correctly

### Goals
- Validate pointer operations (`.adr`, `.val`)
- Check reference type semantics
- Validate `new`/`del` matching

### Key Deliverables
1. **Pointer Type Checking**
   - `.adr` operation creates pointer type
   - `.val` operation dereferences pointer type
   - Pointer arithmetic validation
   - Null pointer checking

2. **Reference Type Semantics**
   - Reference parameter validation
   - `ref T` vs `ptr T` distinction
   - `nil` only for reference types

3. **Memory Management**
   - Track `new` allocations
   - Validate `del` on references
   - `defer` scope validation
   - Memory leak detection (optional)

### Success Metrics
- ✅ Pointer operations type check correctly
- ✅ Reference parameters validated
- ✅ `new`/`del` pairing validated
- ✅ Error count reduced by ~160

### Estimated Examples Fixed
- 011_memory.a7 (remaining pointer errors)
- 013_pointers.a7 (remaining errors)
- 024_defer.a7 (61 errors → ~5)

---

## Phase 6: Advanced Features 🚀
**Priority**: P2 - Medium
**Impact**: Will fix remaining complex example errors
**Target**: All examples 023-035 compile cleanly

### Goals
- Method resolution
- Function pointers
- Complex data structures
- Advanced type scenarios

### Key Deliverables
1. **Method Resolution**
   - Resolve methods on struct instances
   - Type check `self` parameter
   - Method call syntax validation

2. **Function Pointers**
   - Function pointer types
   - Function pointer calls
   - Higher-order functions
   - Callback validation

3. **Complex Data Structures**
   - Linked list pointer chains
   - Tree traversal validation
   - State machine transitions
   - Array algorithm validation

### Success Metrics
- ✅ Method calls resolve correctly
- ✅ Function pointers type check
- ✅ Complex examples compile cleanly
- ✅ Remaining errors < 50 total

### Estimated Examples Fixed
- 017_methods.a7 (72 errors → 0)
- 025_linked_list.a7 (142 errors → ~10)
- 026_binary_tree.a7 (176 errors → ~10)
- 027_callbacks.a7 (133 errors → ~5)
- 028_state_machine.a7 (167 errors → ~5)
- 029_sorting.a7 (192 errors → ~10)

---

## Phase 7: Polish & Edge Cases ✨
**Priority**: P3 - Low
**Impact**: Final cleanup and quality improvements
**Target**: 100% example coverage, excellent error messages

### Goals
- Variable shadowing
- Error message improvements
- Edge case handling
- Test coverage completion

### Key Deliverables
1. **Scope Improvements**
   - Allow variable shadowing in nested scopes
   - Proper closure capture semantics
   - Lifetime analysis (advanced)

2. **Error Quality**
   - More specific error messages
   - Better error span precision
   - Helpful suggestions and fixes
   - Error recovery strategies

3. **Edge Cases**
   - Unicode identifiers
   - Very long expressions
   - Deeply nested scopes
   - Mutual recursion

4. **Test Suite**
   - 100% semantic test coverage
   - All examples compile cleanly
   - Regression test suite
   - Performance benchmarks

### Success Metrics
- ✅ All 36 examples compile without errors
- ✅ 228/228 semantic tests passing (100%)
- ✅ Error messages are clear and actionable
- ✅ Edge cases handled gracefully

### Estimated Examples Fixed
- 032_prime_numbers.a7 (4 errors → 0)
- 033_fibonacci.a7 (111 errors → 0)
- 034_string_utils.a7 (161 errors → 0)
- 035_matrix.a7 (204 errors → 0)

---

## Timeline & Milestones

### Milestone 1: Basic Functionality (Phases 1-2)
**Target**: 2-3 weeks
- Module system working
- Symbol resolution fixed
- Type inference implemented
- Examples 001-015 compile cleanly
- Error reduction: ~80%

### Milestone 2: Type System Complete (Phases 3-4)
**Target**: 1-2 weeks
- Return types validated
- Enums/unions supported
- Examples 016-022 compile cleanly
- Error reduction: ~90%

### Milestone 3: Advanced Features (Phases 5-6)
**Target**: 2-3 weeks
- Pointer operations validated
- Method resolution working
- Complex examples compile
- Error reduction: ~95%

### Milestone 4: Production Ready (Phase 7)
**Target**: 1 week
- All examples compile
- Test suite complete
- Error messages polished
- Error reduction: 100%

**Total Estimated Time**: 6-9 weeks

---

## Current Phase: Phase 1 🎯

We are currently in **Phase 1: Module System & Symbol Resolution**.

**Next Steps**:
1. Implement basic `io` module
2. Fix symbol table parameter registration
3. Test with examples 001-007
4. Move to Phase 2 when basic examples compile

See `TODO.md` for detailed task breakdown.
