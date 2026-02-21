---
layout: ../layouts/DocsLayout.astro
title: Start
description: Install the toolchain and run the first compile.
---

## Requirements

- Python `3.13+`
- [`uv`](https://docs.astral.sh/uv/)
- Zig for building generated `.zig` output

## Install

```bash
git clone https://github.com/airbus5717/a7-py.git
cd a7-py
uv sync
```

## First Compile

```bash
uv run python main.py examples/001_hello.a7
```

This writes `examples/001_hello.zig`.

## Quick Checks

```bash
uv run python main.py --mode tokens examples/006_if.a7
uv run python main.py --mode ast examples/004_func.a7
uv run python main.py --mode semantic examples/009_struct.a7
uv run python main.py --mode pipeline examples/014_generics.a7
```

## Tests

```bash
PYTHONPATH=. uv run pytest
./run_all_tests.sh
```

## Docs Dev

```bash
cd site
npm install
npm run dev
```

Local URL is usually `http://localhost:4321/a7-py/`.
