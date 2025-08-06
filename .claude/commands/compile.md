# A7 Compiler

Compile A7 source files using the a7-py compiler.

## Purpose

This command helps you compile A7 programming language files and test the compiler implementation.

## Usage

```
/compile [file.a7]
```

## What this command does

1. **Compiles A7 source files** using the main.py entry point
2. **Shows compilation output** with rich formatting
3. **Tests parser/tokenizer** functionality
4. **Validates language features** against examples

## Example Commands

### Basic compilation
```bash
# Compile specific A7 file
uv run python main.py examples/001_hello.a7

# Compile with JSON output
uv run python main.py --json examples/001_hello.a7

# Test all examples
for file in examples/*.a7; do echo "=== Testing $file ==="; uv run python main.py "$file" || echo "FAILED: $file"; done
```

### Development workflow
```bash
# Run tests first
uv run pytest

# Test specific A7 language feature
uv run python main.py examples/014_generics.a7

# Debug tokenizer issues
uv run python main.py --debug examples/problematic.a7
```

## A7 Language Features

The compiler supports:
- Variables, functions, control flow
- Structs, enums, unions, generics
- Memory management (new/del/pointers)  
- Pattern matching, defer statements
- Module system and imports

## Best Practices

- Test compilation after parser changes
- Validate against all 22 example files
- Use JSON mode for automated testing
- Check error messages are helpful