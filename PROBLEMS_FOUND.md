# Problems Found in A7 Examples

**Date**: 2025-11-03
**Analysis**: Systematic review of all 36 example files

---

## 🔴 CRITICAL: Invalid `nil` Usage (Spec Violations)

### Problem: `cast(struct, nil)` - Casting nil to value types

**Rule Violated**: `nil` can ONLY be used with reference types (`ref T`), not value types like structs.

**Files Affected** (7 occurrences):

1. **examples/004_func.a7:17**
   ```a7
   ret cast(struct { quotient: i32, remainder: i32 }, nil)
   ```
   - Function: `divide :: fn(a: i32, b: i32) struct {...}`
   - **Fix**: Should return actual struct with computed values:
     ```a7
     ret struct { quotient: i32, remainder: i32 } { quotient: a / b, remainder: a % b }
     ```

2. **examples/023_inline_structs.a7:7**
   ```a7
   ret cast(struct { x: i32, y: i32 }, nil)
   ```
   - Function: `get_point :: fn() struct { x: i32, y: i32 }`
   - **Fix**: `ret struct { x: i32, y: i32 } { x: 10, y: 20 }`

3. **examples/023_inline_structs.a7:13**
   ```a7
   ret cast(struct { sin: f64, cos: f64 }, nil)
   ```
   - Function: `sin_cos :: fn(angle: f64) struct { sin: f64, cos: f64 }`
   - **Fix**: `ret struct { sin: f64, cos: f64 } { sin: 0.0, cos: 1.0 }`

4. **examples/031_number_guessing.a7:77**
   ```a7
   cast(struct { min: i32, max: i32, attempts: i32 }, nil)  // Would be {1, 10, 5}
   ```
   - **Fix**: Use actual values: `struct { min: i32, max: i32, attempts: i32 } { min: 1, max: 10, attempts: 5 }`

5. **examples/031_number_guessing.a7:79**
   ```a7
   cast(struct { min: i32, max: i32, attempts: i32 }, nil)  // Would be {1, 50, 7}
   ```
   - **Fix**: `struct { min: i32, max: i32, attempts: i32 } { min: 1, max: 50, attempts: 7 }`

6. **examples/031_number_guessing.a7:81**
   ```a7
   cast(struct { min: i32, max: i32, attempts: i32 }, nil)  // Would be {1, 100, 10}
   ```
   - **Fix**: `struct { min: i32, max: i32, attempts: i32 } { min: 1, max: 100, attempts: 10 }`

7. **examples/034_string_utils.a7:26**
   ```a7
   ret cast(struct { vowels: i32, consonants: i32 }, nil)
   ```
   - Function: `count_vowels :: fn(text: string) struct { vowels: i32, consonants: i32 }`
   - **Fix**: `ret struct { vowels: i32, consonants: i32 } { vowels: 0, consonants: 0 }`

---

### Problem: `StructType{nil, ...}` - Initializing array fields with nil

**Files Affected** (2 occurrences):

8. **examples/027_callbacks.a7:116**
   ```a7
   EventDispatcher :: struct {
       handlers: [10]EventHandler  // ARRAY, not pointer!
       handler_count: i32
   }
   ...
   dispatcher := EventDispatcher{nil, 0}  // WRONG!
   ```
   - **Fix**: Either omit the field or use proper initialization:
     ```a7
     dispatcher := EventDispatcher{handler_count: 0}  // Named init
     // OR create helper function that properly initializes the array
     ```

9. **examples/033_fibonacci.a7:38**
   ```a7
   FibMemo :: struct {
       cache: [100]i32  // ARRAY, not pointer!
       initialized: bool
   }
   ...
   memo := FibMemo{nil, false}  // WRONG!
   ```
   - **Fix**: Don't use positional initialization for structs with arrays. Use named fields or leave arrays uninitialized:
     ```a7
     memo := FibMemo{initialized: false}  // Array zero-initialized automatically
     ```

---

## ⚠️ MODERATE: Placeholder/Incomplete Implementations

### Problem: Placeholder functions that don't compute real values

10. **examples/034_string_utils.a7:5-26**
    ```a7
    // Count characters in string (placeholder - would use actual string length)
    count_chars :: fn(text: string) i32 {
        ret 0  // Placeholder
    }

    // Simplified word counting (placeholder)
    count_words :: fn(text: string) i32 {
        ret 0  // Placeholder
    }
    ```
    - **Status**: Acceptable for examples but should be noted
    - **Note**: Functions exist but don't implement real logic

---

## 📝 MINOR: Code Quality Issues

### Problem: Struct literal syntax inconsistency

**Good practices in some files**:
- Named field initialization: `Person{name: "John", age: 30}`
- Clear and explicit

**Positional initialization** (error-prone):
- `List{nil, nil, 0}` - requires knowing field order
- Can break if struct definition changes

**Recommendation**: Prefer named field initialization, especially for:
- Structs with >2 fields
- Structs with array/complex fields
- Public APIs

### Files using positional initialization:
- examples/025_linked_list.a7:20 - `List{nil, nil, 0}` ✅ OK (pointer fields)
- examples/026_binary_tree.a7:20 - `BinaryTree{nil, 0}` ✅ OK (pointer field)
- examples/027_callbacks.a7:116 - `EventDispatcher{nil, 0}` ❌ BAD (array field)
- examples/033_fibonacci.a7:38 - `FibMemo{nil, false}` ❌ BAD (array field)

---

## 🔍 TODO Comments in Source Code

11. **src/ast_nodes.py:573**
    ```python
    # TODO: Proper string escape sequence parsing
    ```
    - Not critical but indicates incomplete implementation

---

## Summary Statistics

- **Total Files Reviewed**: 36 examples + source files
- **Critical Issues (Spec Violations)**: 9 instances
  - `cast(struct, nil)`: 7 instances
  - Array field initialized with `nil`: 2 instances
- **Moderate Issues**: 2 instances (placeholder implementations)
- **Minor Issues**: Style/consistency recommendations

---

## Recommended Actions

### Immediate (Critical):
1. ✅ Fix all 7 `cast(struct, nil)` to return proper struct values
2. ✅ Fix 2 struct initializations with nil for array fields

### Short-term (Quality):
3. Consider adding warnings/errors in parser for `cast(struct, nil)` patterns
4. Add linter rule to detect positional struct initialization with >2 fields
5. Implement placeholder string functions if needed for completeness

### Long-term (Documentation):
6. Add section in spec about struct initialization best practices
7. Document that `cast(T, nil)` is only valid when T is a reference type
8. Add examples of proper struct literal syntax patterns

---

## Files Needing Fixes

**Priority 1 - Spec Violations**:
- examples/004_func.a7
- examples/023_inline_structs.a7 (2 occurrences)
- examples/027_callbacks.a7
- examples/031_number_guessing.a7 (3 occurrences)
- examples/033_fibonacci.a7
- examples/034_string_utils.a7

**Total**: 7 files need immediate fixes for 9 spec violations
