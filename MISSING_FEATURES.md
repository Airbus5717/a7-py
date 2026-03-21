# A7 Compiler — Language-Core Gap Snapshot

**Compiler Status**: Full pipeline runs (Tokenizer -> Parser -> Semantic -> Preprocessor -> Codegen).  
**Current Test Status** (`PYTHONPATH=. uv run pytest -q`, 2026-02-24): **1067 passed, 0 failed, 0 skipped**.  
**Examples**: 36/36 pass end-to-end compile + build + run + output verification.

---

## Recently Completed (Language Core)

1. `match` expressions are type-checked and participate in expression typing.
2. `@type_set(...)` parses in value context.
3. Generic arithmetic and generic local literal initialization are relaxed where valid.
4. Generic struct literal field checks substitute concrete type arguments.
5. Field access resolves concrete struct layout for generic instances.
6. Match semantics now enforce:
   - pattern type compatibility with the scrutinee,
   - bool/enum exhaustiveness (or explicit `else` / wildcard),
   - wildcard pattern parsing (`case _:`),
   - return-path correctness for exhaustive enum/bool `match` without `else`.

---

## Remaining Language-First Gaps

1. **`fall` statement semantics**
   - `fall` is parsed (`NodeKind.FALL`) but not yet validated or lowered in semantic/codegen passes.

2. **Advanced match diagnostics**
   - No overlap/redundancy diagnostics for case patterns.
   - No unreachable-branch detection for wildcard-first or fully-covered prior patterns.

3. **Memory/lifetime model**
   - Current validation covers basic `del` reference checks.
   - Ownership/borrow-style lifetime guarantees are not implemented.

4. **Generic constraint internals**
   - Inline type-set constraint resolution in `src/generics.py` is still placeholder-level (`resolve_generic_constraint`).

5. **Backend semantic parity hardening**
   - Core conformance is green, but differential/backend-equivalence checks should be expanded and kept mandatory for new language features.

---

## Out of Scope for This Snapshot

- Package ecosystem, registry/distribution workflows, and broader tooling are intentionally secondary to language-core correctness.
