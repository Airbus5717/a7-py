# A7 Example Programs

This directory contains 36 example programs demonstrating A7 language features and practical applications.

## Basic Language Features (000-010)

- **000_empty.a7** - Minimal valid A7 program
- **001_hello.a7** - Hello World
- **002_var.a7** - Variables and constants
- **003_comments.a7** - Comment syntax
- **004_func.a7** - Function declarations and calls
- **005_for_loop.a7** - For loops (C-style and range-based)
- **006_if.a7** - If/else conditionals
- **007_while.a7** - While loops
- **008_switch.a7** - Match/switch statements
- **009_struct.a7** - Struct declarations
- **010_enum.a7** - Enum types

## Advanced Features (011-021)

- **011_memory.a7** - Memory management (new, del, defer)
- **012_arrays.a7** - Array operations
- **013_pointers.a7** - Property-based pointer syntax (.adr, .val)
- **014_generics.a7** - Generic functions and types
- **015_types.a7** - Type system overview
- **016_unions.a7** - Union types
- **017_methods.a7** - Methods and member functions
- **018_modules.a7** - Module system and imports
- **019_literals.a7** - Literal syntax
- **020_operators.a7** - Operator precedence and usage
- **021_control_flow.a7** - Complete control flow patterns

## Feature Demonstrations (022-029)

**Recently Implemented Features:**

- **022_function_pointers.a7** - Function pointers and higher-order functions
- **023_inline_structs.a7** - Inline/anonymous struct types
- **024_defer.a7** - Resource management with defer
- **025_linked_list.a7** - Generic linked list implementation
- **026_binary_tree.a7** - Binary search tree with traversal
- **027_callbacks.a7** - Event handling and callbacks
- **028_state_machine.a7** - State machines with function pointers
- **029_sorting.a7** - Sorting algorithms with comparators

## Practical Applications (030-035)

**Real-World Programs:**

- **030_calculator.a7** - Scientific calculator with sqrt, power, percentage
- **031_number_guessing.a7** - Interactive guessing game with RNG
- **032_prime_numbers.a7** - Sieve of Eratosthenes, prime factorization
- **033_fibonacci.a7** - Fibonacci with multiple implementations
- **034_string_utils.a7** - String processing and text utilities
- **035_matrix.a7** - Matrix operations and linear algebra

## Running Examples

```bash
# Single example
uv run python main.py examples/001_hello.a7

# All examples
for file in examples/*.a7; do
    echo "Testing $file"
    uv run python main.py "$file"
done
```

## Example Categories

### Learning Path

1. Start with basics (000-010): language syntax
2. Explore advanced features (011-021): pointers, generics, modules
3. Study feature demos (022-029): modern language features
4. Build practical programs (030-035): real applications

### By Difficulty

- **Beginner**: 000-010 (language fundamentals)
- **Intermediate**: 011-021 (advanced features)
- **Advanced**: 022-029 (modern patterns)
- **Practical**: 030-035 (complete programs)

### By Topic

- **Data Structures**: 025 (linked list), 026 (binary tree)
- **Algorithms**: 029 (sorting), 032 (primes), 033 (fibonacci)
- **Patterns**: 027 (callbacks), 028 (state machine)
- **Applications**: 030 (calculator), 031 (game), 035 (matrix)

## Contributing Examples

When adding new examples:

1. Use sequential numbering (036, 037, etc.)
2. Include comprehensive comments
3. Demonstrate A7 idioms and best practices
4. Test that it parses successfully
5. Update this README

## Example Quality

All examples in this directory:

- Parse successfully with the A7 compiler
- Include clear comments explaining features
- Follow A7 style conventions
- Demonstrate practical or educational concepts
- Are self-contained and runnable
