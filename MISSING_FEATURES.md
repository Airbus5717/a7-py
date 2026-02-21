# A7 Compiler — Feature Status & Roadmap

**Compiler Status**: Full pipeline working (Tokenizer → Parser → Semantic → Preprocessor → Zig Codegen)
**Tests**: 983 passing, 9 skipped
**Examples**: 36/36 pass end-to-end compile + build + run + output verification

---

## Completed Features

### Parser — 100% Complete
All A7 language constructs parse correctly: functions, structs, enums, unions, generics (`$T`), type sets, variadic functions, builtin intrinsics, match patterns, inline structs, function types, all import variants.

### Semantic Analysis — 3-Pass Pipeline
- **Pass 1**: Name resolution with hierarchical scopes
- **Pass 2**: Type checking with inference, generic type inference
- **Pass 3**: Semantic validation (control flow, memory, nil checks)

### AST Preprocessing — 9 Sub-Passes
All iterative (no recursion): `.adr`/`.val` lowering, stdlib resolution, struct init normalization, mutation analysis, usage analysis, type inference, shadowing resolution, nested function hoisting, constant folding.

### Standard Library Registry
`src/stdlib/` with io (println, print, eprintln) and math (sqrt, abs, floor, ceil, sin, cos, tan, log, exp, min, max) modules. Backend-specific mappings.

### Zig Code Generation — All Node Types
Type mapping, I/O special-casing, memory management, nested function hoisting, var/const inference, variable shadowing prevention, generic struct wrapping.

### Architecture Quality
- All AST traversals are iterative (no recursion) — works with Python recursion limit of 100
- AST node annotations (`is_mutable`, `is_used`, `emit_name`, `resolved_type`, `hoisted`, `stdlib_canonical`) bridge preprocessor and backends

---

## Known Gaps (Current)

No example is currently blocked in the end-to-end verification harness. Remaining work is focused on language/runtime depth and breadth rather than baseline compile/build/run stability.

---

## Deferred Features

### Labeled Loops
```a7
outer: for i := 0; i < 10; i += 1 {
    break outer
}
```
AST has `label` field reserved. Deferred due to syntax ambiguity (`label: type` vs `variable: type`).

### Array Programming Library (Spec Section 9)
Tensor types, broadcasting, reductions, linear algebra, AI primitives. These are standard library features, not parser/compiler features.

### Alternative Backends
C backend, native codegen — future work. Architecture supports pluggable backends via `src/backends/base.py`.

---

## Next Steps (Priority Order)

1. **Expand semantic depth** — richer generic inference and advanced function-type validation
2. **Stdlib implementation** — actual `.a7` stdlib modules (`std/io`, `std/math`, etc.) beyond backend mappings
3. **Alternative backends** — C/native backends on top of `src/backends/base.py`
4. **More behavioral tests** — broaden output-level golden verification beyond examples into targeted semantic scenarios
