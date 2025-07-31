# A7 Programming Language Compiler

This is a Python implementation of a compiler for the A7 programming language.
A7 is a statically-typed, procedural language with C-style syntax, manual 
memory management, and compile-time generics.

## Building

```bash
uv sync
```

## Running

```bash
python main.py <file.a7>
```

Or use the shell script:

```bash
./run.sh <file.a7>
```

## Testing

```bash
uv run pytest
```

The compiler currently implements a complete lexer/tokenizer. Parser and code
generation are not yet implemented.

A7 programs use the `.a7` file extension. See the `examples/` directory for 
sample programs demonstrating language features.

The language specification is in `docs/SPEC.md`. Implementation guidance for
this codebase is in `CLAUDE.md`.

## Dependencies

- Python 3.13+
- uv (for package management)
- pytest (for testing)
- rich (for terminal output)

The compiler is designed to target Zig as the output language.

This is work in progress. Contributions welcome.