# A7 Compiler — Missing Features Snapshot

**Compiler Status**: Full pipeline runs (Tokenizer → Parser → Semantic → Preprocessor → Zig Codegen).  
**Current Test Status** (`PYTHONPATH=. uv run pytest`, 2026-02-21): **1039 passed, 7 failed, 0 skipped**.  
**Examples**: 36/36 pass end-to-end compile + build + run + output verification.

---

## Newly Unskipped Semantic Gaps

The 9 previously skipped semantic tests were unskipped. Two now pass; seven fail and define the current missing work. Those failures collapse into six implementation areas below.

1. **Match expressions are parsed but not type-checked**
   - Failing test: `test/test_semantic_control_flow.py:434`
   - Current error: `Unknown expression kind: NodeKind.MATCH_EXPR`
   - Needed:
     - Add `MATCH_EXPR` handling in `TypeCheckingPass._visit_expression_impl`.
     - Type-check each case arm expression and `else` expression.
     - Enforce arm type compatibility and return unified expression type.

2. **`@type_set(...)` in value context does not parse correctly**
   - Failing test: `test/test_semantic_generics.py:159`
   - Current error: `Expected expression` at first type argument token (`i8`).
   - Needed:
     - Treat `@type_set` as a type-taking builtin when parsed as expression, or
     - Parse `@type_set(...)` declarations through a dedicated type-set declaration path.

3. **Generic arithmetic in function bodies is too strict without constraint flow**
   - Failing test: `test/test_semantic_generics.py:176`
   - Current error: `Requires numeric type` for `$T * 2`.
   - Needed:
     - Propagate generic constraints (or inferred concrete type bindings) into expression checking.
     - Allow arithmetic when `$T` is known numeric by constraint or call-site inference.

4. **Generic struct literal field checks do not substitute type arguments**
   - Failing test: `test/test_semantic_generics.py:248`
   - Current error: `Type mismatch: expected '$T', got 'i32'`.
   - Needed:
     - Instantiate/substitute struct field types for `Pair(i32, string){...}` before field validation.

5. **Field access on generic struct instances is unresolved**
   - Failing tests:
     - `test/test_semantic_generics.py:263`
     - `test/test_semantic_generics.py:434`
   - Current error: `Cannot access field on non-struct type: got 'Box(i32)'` / `Node(i32)`.
   - Needed:
     - Resolve `GenericInstanceType` to concrete `StructType` during field access.
     - Support recursive generic instantiation safely (cycle-aware resolution for recursive types).

6. **Literal initialization for generic locals lacks inference/coercion**
   - Failing test: `test/test_semantic_generics.py:311`
   - Current error: `Type mismatch: expected '$T', got 'i32'` for `total: $T = 0`.
   - Needed:
     - Permit numeric literal initialization for generic numeric variables, or
     - Specialize generic function body typing from call-site type mapping before local checks.

---

## Deferred (Still Planned)

1. Labeled loops (`outer: for ...`) with syntax disambiguation.
2. Array-programming stdlib (tensor/broadcast/linear algebra features).
3. Alternative backends (C/native) using `src/backends/base.py`.
