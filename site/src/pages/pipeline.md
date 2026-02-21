---
layout: ../layouts/DocsLayout.astro
title: Pipeline
description: How source code moves through each compiler stage.
---

## Stage Flow

```text
Source (.a7) -> Tokenizer -> Parser -> Semantic Passes -> AST Preprocessing -> Zig Codegen
```

## Stage 1 Tokenizer

Tokenizer converts source text into tokens.

It handles nested comments, numeric forms, and generic tokens like `$T`.

## Stage 2 Parser

Parser builds the AST with recursive descent and precedence rules.

It parses declarations, statements, and expressions.

## Stage 3 Semantic Passes

The semantic layer runs three passes.

1. Name resolution with scope tracking.
2. Type checking and inference.
3. Semantic validation for flow and memory rules.

## Stage 4 AST Preprocessing

Preprocessing normalizes the AST before backend generation.

Current passes include pointer helper lowering, stdlib resolution, mutation analysis, usage analysis, shadowing resolution, nested function hoisting, and constant folding.

## Stage 5 Zig Codegen

Codegen maps the processed AST to Zig output.

It performs output naming, type mapping, and code emission.

## Debug Workflow

Use a lower mode first.

Move up only after the current stage looks correct.

```bash
uv run python main.py --mode tokens examples/013_pointers.a7
uv run python main.py --mode ast examples/013_pointers.a7
uv run python main.py --mode semantic examples/013_pointers.a7
uv run python main.py examples/013_pointers.a7
```
