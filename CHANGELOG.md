# Changelog

All notable changes to the A7 compiler will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
- Parser completeness increased from 65% to 72%
- Test count increased from 363 to 411 tests (100% passing, 0 skipped)
- Type system completeness increased from 67% to 89%
- Updated TokenType.STRUCT to be recognized in function return type parsing
- Improved documentation in README.md, TODOLIST.md, and MISSING_FEATURES.md

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
