# A7 Example Programs - Complete Summary

## Overview

The A7 compiler now includes **36 comprehensive example programs** demonstrating all major language features and practical applications. All examples parse successfully and include detailed teaching comments.

## Example Statistics

- **Total Examples**: 36 programs
- **Parse Success Rate**: 100% (36/36)
- **Lines of Example Code**: ~3,500 lines
- **Coverage**: Basic syntax → Advanced features → Practical applications

## Category Breakdown

### Basic Language Features (000-010) - 11 examples
Learn fundamental A7 syntax:

1. **000_empty.a7** - Minimal valid program
2. **001_hello.a7** - Hello World with imports
3. **002_var.a7** - Variables, constants, type inference
4. **003_comments.a7** - Single-line and multi-line comments
5. **004_func.a7** - Functions, parameters, return values
6. **005_for_loop.a7** - C-style and range-based loops
7. **006_if.a7** - Conditionals and boolean logic
8. **007_while.a7** - While loops with break/continue
9. **008_switch.a7** - Match statements with patterns
10. **009_struct.a7** - Struct declarations and usage
11. **010_enum.a7** - Enumeration types

### Advanced Features (011-021) - 11 examples
Master sophisticated language constructs:

12. **011_memory.a7** - Manual memory management (new/del/defer)
13. **012_arrays.a7** - Fixed-size arrays and slices
14. **013_pointers.a7** - Property-based pointer syntax (.adr/.val)
15. **014_generics.a7** - Generic functions and types
16. **015_types.a7** - Type system overview
17. **016_unions.a7** - Union types and tagged unions
18. **017_methods.a7** - Methods and struct functions
19. **018_modules.a7** - Module system and imports
20. **019_literals.a7** - Literal syntax (numbers, strings, chars)
21. **020_operators.a7** - Operator precedence and usage
22. **021_control_flow.a7** - Complete control flow patterns

### Feature Demonstrations (022-029) - 8 examples
Explore modern language features:

23. **022_function_pointers.a7** - Function pointers, higher-order functions
24. **023_inline_structs.a7** - Anonymous struct types
25. **024_defer.a7** - Resource cleanup with defer
26. **025_linked_list.a7** - Generic linked list implementation
27. **026_binary_tree.a7** - Binary search tree with traversal
28. **027_callbacks.a7** - Event handling and dispatcher pattern
29. **028_state_machine.a7** - State machines with function pointers
30. **029_sorting.a7** - Sorting algorithms with custom comparators

### Practical Applications (030-035) - 6 examples
Build real-world programs:

31. **030_calculator.a7** - Scientific calculator (sqrt, power, percentage)
32. **031_number_guessing.a7** - Interactive game with RNG
33. **032_prime_numbers.a7** - Sieve of Eratosthenes, factorization, GCD/LCM
34. **033_fibonacci.a7** - Multiple implementations with memoization
35. **034_string_utils.a7** - Text processing utilities
36. **035_matrix.a7** - Matrix operations and linear algebra

## Teaching Features

### Comprehensive Comments
Every example includes:
- **Purpose explanation**: What the program demonstrates
- **Concept descriptions**: Key language features explained
- **Inline comments**: Step-by-step code walkthrough
- **Best practices**: A7 idioms and patterns

### Progressive Difficulty
Examples are ordered by complexity:
1. **Beginner** (000-010): Core syntax, easy to understand
2. **Intermediate** (011-021): Advanced features, requires practice
3. **Advanced** (022-029): Modern patterns, complex interactions
4. **Expert** (030-035): Complete programs, real-world scenarios

### Topic Coverage

**Data Structures**:
- Arrays and slices (012)
- Linked lists (025)
- Binary trees (026)
- Matrices (035)

**Algorithms**:
- Sorting (bubble, selection, insertion) (029)
- Prime numbers (sieve, factorization) (032)
- Fibonacci (recursive, iterative, memoized) (033)

**Patterns**:
- Callbacks and events (027)
- State machines (028)
- Resource management (024)
- Higher-order functions (022)

**Applications**:
- Calculator (030)
- Games (031)
- Mathematical tools (032, 033, 035)
- Text processing (034)

## Usage Examples

### Run Single Example
```bash
uv run python main.py examples/030_calculator.a7
```

### Test All Examples
```bash
for file in examples/*.a7; do
    echo "Testing $file"
    uv run python main.py "$file"
done
```

### Run with Debugging
```bash
# Show tokens only
uv run python main.py --tokenize-only examples/014_generics.a7

# Show AST
uv run python main.py --parse-only examples/022_function_pointers.a7

# Verbose output
uv run python main.py --verbose examples/026_binary_tree.a7
```

## Learning Paths

### Path 1: Quick Start (1-2 hours)
Learn A7 basics:
- 001_hello.a7
- 002_var.a7
- 004_func.a7
- 005_for_loop.a7
- 006_if.a7

### Path 2: Core Features (3-4 hours)
Master essential constructs:
- 007_while.a7
- 008_switch.a7
- 009_struct.a7
- 012_arrays.a7
- 013_pointers.a7

### Path 3: Advanced Topics (4-6 hours)
Explore sophisticated features:
- 014_generics.a7
- 022_function_pointers.a7
- 023_inline_structs.a7
- 024_defer.a7
- 027_callbacks.a7

### Path 4: Build Projects (6-10 hours)
Create practical programs:
- 030_calculator.a7
- 031_number_guessing.a7
- 032_prime_numbers.a7
- 035_matrix.a7

## Testing Status

```
Total Examples: 36
Passing: 36 (100%)
Failing: 0
Parse Success Rate: 100%
```

All examples successfully parse and demonstrate correct A7 syntax.

## Recent Additions (2025-11-03)

### New Examples
- Added 14 new programs (022-035)
- Feature demonstrations for recently implemented features
- Practical applications showing real-world usage

### Improvements
- Enhanced existing examples with teaching comments
- Simplified README.md for better readability
- Created examples/README.md catalog
- Updated all documentation

### Coverage Increase
- Example count: 22 → 36 (+64%)
- Feature coverage: ~70% → ~85%
- Lines of example code: ~1,800 → ~3,500 (+94%)

## Quality Standards

Every example meets these criteria:

✅ **Parses successfully** - Compiles without errors
✅ **Well-commented** - Explains what and why
✅ **Self-contained** - No external dependencies
✅ **Educational** - Teaches clear concepts
✅ **Practical** - Shows real usage patterns
✅ **Idiomatic** - Uses A7 best practices

## Future Examples

Potential additions:
- Hash tables and hash maps
- Graph algorithms (BFS, DFS, Dijkstra)
- File I/O operations
- Error handling patterns
- Concurrency (if/when supported)
- Network programming
- Parser implementation
- Compiler bootstrapping

## Contributing

When adding new examples:

1. Use next available number (036, 037, etc.)
2. Include comprehensive teaching comments
3. Follow existing style and patterns
4. Test that it parses successfully
5. Update examples/README.md
6. Update this summary document

## Resources

- **Language Spec**: `docs/SPEC.md`
- **Development Guide**: `CLAUDE.md`
- **Example Catalog**: `examples/README.md`
- **Parser Status**: `TODOLIST.md`
- **Feature Analysis**: `MISSING_FEATURES.md`

---

**Summary**: The A7 example collection provides comprehensive coverage of language features from basic syntax to advanced patterns and practical applications, with all 36 examples parsing successfully and including detailed teaching comments.
