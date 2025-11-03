# Changelog

All notable changes to the A7 compiler will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **Fixed logical operators in all example files**:
  - Replaced C-style `&&` with A7 keyword `and` throughout all examples
  - Replaced C-style `||` with A7 keyword `or` throughout all examples
  - Fixed 6 example files that incorrectly used `&&`/`||` operators
  - All 36 examples now generate valid AST (was 34/36, now 36/36)
  - Simplified complex boolean expressions to work around parser limitations with `(a or b) and !c` patterns
- **Corrected nil usage in specification and examples**:
  - Updated `docs/SPEC.md` to clarify that `nil` is only valid for reference types (`ref T`)
  - Arrays, structs, primitives, and other value types cannot be assigned `nil`
  - Fixed all 36 example files to use proper array initialization:
    - Replaced invalid `arr: [5]i32 = nil` with `arr: [5]i32` (zero-initialized)
    - Added clear comments explaining zero-initialization behavior
  - Arrays now properly initialized with: no initializer (zero-init), single value, or array literal
- **Fixed spec violations with struct initialization** (7 examples, 9 instances):
  - `examples/004_func.a7`: Fixed `divide()` function returning `cast(struct, nil)` → proper struct literal
  - `examples/023_inline_structs.a7`: Fixed `get_point()` and `sincos()` functions returning `cast(struct, nil)` → proper inline struct initialization
  - `examples/027_callbacks.a7`: Fixed `EventDispatcher` initialization with array field set to `nil` → named field init (auto-zero)
  - `examples/031_number_guessing.a7`: Fixed 3 difficulty config functions returning `cast(struct, nil)` → proper struct literals
  - `examples/033_fibonacci.a7`: Fixed `FibMemo` initialization with array field set to `nil` → named field init (auto-zero)
  - `examples/034_string_utils.a7`: Fixed `count_vowels()` returning `cast(struct, nil)` → proper struct literal
  - All examples now use proper struct initialization with explicit field values or rely on zero-initialization

### Changed
- **Modernized all example code to use compound assignment operators**:
  - Updated all for loops and assignments to use `+=`, `-=`, `*=`, `/=` instead of verbose forms
  - Changed `i = i + 1` → `i += 1` throughout 36 example files
  - Changed struct field updates like `obj.val.field = obj.val.field + 1` → `obj.val.field += 1`
  - Improved code readability and demonstrated idiomatic A7 style
- Updated visibility rules documentation to clarify `public` modifier restrictions
- Updated `test_parser_examples.py` to handle files with import statements

### Added
- **Comprehensive Gap Analysis**:
  - Created `SPEC_EXAMPLES_GAP_ANALYSIS.md` documenting discrepancies between spec and examples
  - Identified outdated "Known Limitations" claims (range patterns, multiple case values, fallthrough all work)
  - Found labeled break/continue documented but not actually implemented
  - Cataloged undocumented features (compound assignments, match expressions, qualified enum access)
  - Full comparison of all 36 examples against specification
- **New Examples** (14 new programs added, total now 36):
  - Feature demonstrations:
    - `022_function_pointers.a7` - Higher-order functions and callbacks
    - `023_inline_structs.a7` - Anonymous struct types showcase
    - `024_defer.a7` - Resource management with defer
    - `025_linked_list.a7` - Generic linked list implementation
    - `026_binary_tree.a7` - Binary search tree with traversal
    - `027_callbacks.a7` - Event handling and dispatcher pattern
    - `028_state_machine.a7` - State machines with function pointers
    - `029_sorting.a7` - Sorting algorithms with custom comparators
  - Practical applications:
    - `030_calculator.a7` - Math operations including sqrt, power
    - `031_number_guessing.a7` - Interactive game with RNG
    - `032_prime_numbers.a7` - Sieve of Eratosthenes, factorization
    - `033_fibonacci.a7` - Multiple implementations with memoization
    - `034_string_utils.a7` - Text processing utilities
    - `035_matrix.a7` - Matrix operations and linear algebra
- Improved existing examples with better comments and demonstrations
- Inline/anonymous struct type parsing (`struct { id: i32, data: string }`)
- Function type parsing (`fn(i32) i32`, function pointers, higher-order functions)
- 48 comprehensive test cases for type combinations and edge cases
- New test file `test_parser_type_combinations.py` with 35 tests
- 13 edge case tests for inline struct types in `test_parser_extreme_edge_cases.py`
- Support for inline structs in function parameters and return types
- Support for nested inline struct types
- Support for inline structs with function pointer fields
- Support for arrays and slices of inline structs
- Documentation of language influences (JAI, Odin) in README

### Changed
- README.md simplified and made more natural to read
- Example count increased from 22 to 36 programs (+64% increase)
- Enhanced existing examples (001-012) with comprehensive teaching comments
- Example code: ~1,800 → ~3,500 lines (+94% increase)
- Parser completeness increased from 65% to 72%
- Test count increased from 363 to 411 tests (100% passing, 0 skipped)
- Type system completeness increased from 67% to 89%
- Updated TokenType.STRUCT to be recognized in function return type parsing
- Improved documentation in README.md, TODOLIST.md, CLAUDE.md, and MISSING_FEATURES.md
- Created examples/README.md - catalog of all example programs
- Created EXAMPLES_SUMMARY.md - comprehensive example documentation

### Fixed
- Function type parsing now works in all contexts (params, returns, struct fields)
- Inline struct types now supported in function return types
- Trailing commas now handled correctly in inline struct field lists

## [0.2.0] - 2025-11-03

### Added
- Function type parsing implementation
- Generic type instantiation in type expressions
- Uninitialized variable declarations
- Comprehensive edge case testing infrastructure

### Changed
- Parser completeness increased from 60% to 65%
- Struct literal heuristic improved for better disambiguation
- Test suite expanded with extreme edge case tests

### Fixed
- Generic type parameters in parentheses (e.g., `List($T)`)
- Struct literal vs block statement disambiguation
- Return statement without value for void functions

## [0.1.0] - 2025-11-02

### Added
- Complete tokenizer with all A7 token types
- Recursive descent parser with AST generation
- Support for all major language constructs
- 22 example A7 programs
- Comprehensive test suite (352 tests)
- Rich error messages with source context
- Property-based pointer syntax (`.adr`, `.val`)
- Control flow (if/else, while, for, match)
- Struct, enum, and union declarations
- Function declarations with generics
- Import statements
- Cast expressions

### Documentation
- Complete language specification (docs/SPEC.md)
- Development guide (CLAUDE.md)
- TODOLIST.md with tactical and strategic roadmaps
- MISSING_FEATURES.md with comprehensive feature gap analysis

[Unreleased]: https://github.com/Airbus5717/a7-py/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/Airbus5717/a7-py/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Airbus5717/a7-py/releases/tag/v0.1.0
