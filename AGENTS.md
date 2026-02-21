# Repository Guidelines

## Project Structure & Module Organization
Core compiler code lives in `src/`:
- `src/tokens.py`, `src/parser.py`, `src/ast_nodes.py` for lexing/parsing/AST.
- `src/passes/` for semantic analysis (`name_resolution.py`, `type_checker.py`, `semantic_validator.py`).
- `src/formatters/` for console/JSON output and `src/backends/` for backend interfaces.

Tests are in `test/` and are organized by subsystem (for example `test_parser_*`, `test_semantic_*`, `test_tokenizer_*`). Language samples are in `examples/` (`*.a7`). Specs and reference docs are in `docs/`, especially `docs/SPEC.md`.

## Build, Test, and Development Commands
- `uv sync` installs dependencies for Python 3.13+.
- `uv run python main.py examples/001_hello.a7` runs the compiler.
- `uv run python main.py --tokenize-only examples/006_if.a7` runs lexer-only mode.
- `uv run python main.py --parse-only examples/004_func.a7` runs lexer+parser only.
- `PYTHONPATH=. uv run pytest` runs the full test suite.
- `./test.sh -k generic -v` runs targeted tests through the repo wrapper.
- `./run_all_tests.sh` prints a compact summary across parser/tokenizer/semantic groups.

## Coding Style & Naming Conventions
Use 4-space indentation and follow existing Python/PEP 8 style. Keep modules and functions `snake_case`, classes `PascalCase`, constants `UPPER_CASE`. Prefer explicit type hints on public functions and pass interfaces.

Match existing compiler naming patterns (for example parser helpers like `parse_*_expression`, `parse_*_statement`; semantic pass entry points like `analyze`). Keep new logic in the appropriate subsystem rather than adding cross-cutting code in `main.py`.

## Testing Guidelines
Use `pytest`. Name files `test/test_<area>_<scope>.py`, test functions `test_*`, and group related assertions in `Test*` classes when helpful. Add both success-path and error-path coverage for parser/semantic changes. Run focused tests first, then full suite before opening a PR.

## Commit & Pull Request Guidelines
Recent history uses conventional prefixes: `feat:`, `fix:`, `test:`, `chore:`. Keep commit subjects concise and imperative.

PRs should include:
- what changed and why,
- linked issue(s) when available,
- test commands executed and results.

For feature or behavior changes, update `CHANGELOG.md` and relevant docs (for example `MISSING_FEATURES.md`, `docs/SPEC.md`) in the same PR.
