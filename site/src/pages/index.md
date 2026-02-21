---
layout: ../layouts/DocsLayout.astro
title: A7 Documentation
description: Clear docs for the A7 language and compiler pipeline.
---

This site is built from scratch.

It uses one design system.

It follows one writing style.

<div class="kpi-grid">
  <section class="kpi">
    <p class="value">36</p>
    <p class="label">Runnable examples</p>
  </section>
  <section class="kpi">
    <p class="value">5</p>
    <p class="label">Compiler stages</p>
  </section>
  <section class="kpi">
    <p class="value">983</p>
    <p class="label">Passing tests in current report</p>
  </section>
</div>

## Read In This Order

<div class="doc-cards">
  <a class="doc-card" href="./start/">
    <h3>Start</h3>
    <p>Install dependencies and compile the first file.</p>
  </a>
  <a class="doc-card" href="./cli/">
    <h3>CLI</h3>
    <p>Use the command interface with the right mode and format.</p>
  </a>
  <a class="doc-card" href="./pipeline/">
    <h3>Pipeline</h3>
    <p>Trace tokenizer, parser, semantic passes, preprocessing, and codegen.</p>
  </a>
  <a class="doc-card" href="./language/">
    <h3>Language</h3>
    <p>See types, expressions, control flow, functions, generics, and memory.</p>
  </a>
  <a class="doc-card" href="./examples/">
    <h3>Examples</h3>
    <p>Find what each sample program teaches.</p>
  </a>
  <a class="doc-card" href="./topics/">
    <h3>Topics</h3>
    <p>Read inline examples grouped by topic.</p>
  </a>
  <a class="doc-card" href="./status/">
    <h3>Status</h3>
    <p>Check current coverage and deferred work.</p>
  </a>
  <a class="doc-card" href="./visuals/">
    <h3>Visuals</h3>
    <p>Open large visual references for fast orientation.</p>
  </a>
</div>

## Scope

These docs cover the compiler and language.

They do not market the project.

They focus on commands, behavior, and examples.

## Source Of Truth

- `README.md`
- `docs/SPEC.md`
- `examples/*.a7`
- `MISSING_FEATURES.md`
- `CHANGELOG.md`
