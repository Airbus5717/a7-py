---
layout: ../layouts/DocsLayout.astro
title: CLI
description: Command shape, flags, modes, output formats, and exit codes.
---

## Command Shape

```bash
uv run python main.py [options] <input.a7>
```

`<input.a7>` is required.

## Main Options

| Option | Values | Purpose |
| --- | --- | --- |
| `--mode` | `tokens`, `ast`, `semantic`, `pipeline`, `compile`, `doc` | Selects pipeline stage output. |
| `--format` | `human`, `json` | Changes output shape for people or tools. |
| `--output` | file path | Writes generated backend output to an explicit path. |
| `--doc-out` | `auto` or file path | Writes markdown compilation docs. |
| `--backend` | `zig` | Selects backend implementation. |
| `--verbose` | flag | Prints detailed stage details. |

## Mode Examples

```bash
uv run python main.py --mode tokens examples/006_if.a7
uv run python main.py --mode ast examples/004_func.a7
uv run python main.py --mode semantic examples/009_struct.a7
uv run python main.py --mode pipeline examples/014_generics.a7
uv run python main.py --mode compile examples/001_hello.a7
uv run python main.py --mode doc examples/001_hello.a7
```

## Format Examples

```bash
uv run python main.py --format human examples/014_generics.a7
uv run python main.py --format json examples/014_generics.a7
```

## Documentation Output

```bash
uv run python main.py examples/001_hello.a7 --mode compile --doc-out auto
uv run python main.py examples/001_hello.a7 --mode compile --doc-out out.md
```

`auto` writes docs next to generated output.

## Exit Codes

| Code | Meaning |
| --- | --- |
| `0` | Success |
| `2` | Usage error |
| `3` | File or IO error |
| `4` | Tokenizer error |
| `5` | Parser error |
| `6` | Semantic error |
| `7` | Codegen error |
| `8` | Internal error |

## Automation Note

Use `--format json` with exit codes for CI and scripts.
