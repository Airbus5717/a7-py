# A7 Language-Core Implementation Plan

## Objective
Ship a language-focused preview where syntax, semantics, typing, and backend behavior are stable and conformance-tested.

## Acceptance Criteria
- Core grammar/AST forms are stable and tested.
- Type checker enforces generic + control-flow semantics for supported features.
- Match semantics are type-safe and exhaustive where required.
- C and Zig backend outputs are behaviorally aligned on language conformance tests.

## Milestones

### M1. Grammar and AST Stability
- Freeze core syntax forms in parser tests.
- Keep AST node contracts explicit for declarations, expressions, and patterns.

### M2. Name Resolution and Scope Semantics
- Ensure scope transitions are deterministic for blocks, loops, and match branches.
- Keep symbol-table behavior stable under nested control flow.

### M3. Type-System Completion
- Finalize generic constraints, substitutions, and inference behavior.
- Enforce assignment/call/operator compatibility without unsound fallbacks.

### M4. Match Semantics
- Enforce pattern type compatibility.
- Enforce bool/enum exhaustiveness (or else/wildcard branch).
- Ensure exhaustive match contributes to return-path analysis.

### M5. Memory/Lifetime Semantics
- Move beyond basic `new`/`del` shape checks to explicit ownership/lifetime rules.
- Define boundary behavior for references and FFI interactions.

### M6. IR/Backend Semantic Parity
- Keep semantic behavior consistent across C and Zig backends.
- Add differential checks for language features as they are added.

## Implemented in This Iteration
- Added wildcard pattern parsing (`case _:`).
- Added match pattern type checking in semantic type checking.
- Added bool/enum exhaustiveness checks for match statements and match expressions.
- Added return-path support for exhaustive enum/bool matches without `else`.
- Added tests for wildcard parsing, pattern type mismatch, exhaustiveness, and return-path behavior.

## Next Implementation Slice
- Add `fall` semantic rules and backend lowering.
- Add unreachable/overlap diagnostics for match patterns.
- Start explicit lifetime rule design and validation tests.
