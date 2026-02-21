---
layout: ../layouts/DocsLayout.astro
title: Status
description: Current implementation status and deferred feature list.
---

<div class="kpi-grid">
  <section class="kpi">
    <p class="value">983</p>
    <p class="label">Tests passing</p>
  </section>
  <section class="kpi">
    <p class="value">36 / 36</p>
    <p class="label">Examples passing end to end</p>
  </section>
  <section class="kpi">
    <p class="value">5</p>
    <p class="label">Implemented compiler stages</p>
  </section>
</div>

## Delivered

- Full tokenizer, parser, semantic passes, preprocessing, and Zig code generation.
- Iterative AST traversals in compiler passes.
- Generic parsing and semantic support for current test surface.
- Standard library registry hooks for `std/io` and `std/math` mapping.

## Deferred

### Labeled Loops

Syntax support is deferred.

AST has reserved shape for label fields.

### Array Programming Library Depth

Tensor and broadcasting APIs are deferred.

This belongs to runtime and stdlib depth, not parser readiness.

### Alternative Backends

C backend and native backend are deferred.

Backend abstraction exists under `src/backends/base.py`.

## Current Priority

1. Deepen semantic checks for advanced generics and function types.
2. Expand stdlib behavior beyond symbol mapping.
3. Add broader golden output tests.
