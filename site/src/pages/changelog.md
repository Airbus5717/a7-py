---
layout: ../layouts/DocsLayout.astro
title: Changelog
description: High level release notes for the docs site.
---

Source file is `CHANGELOG.md` in the repository root.

## Unreleased

### Added

- Error stage verifier script and matrix tests.
- End to end example verifier with golden output checks.
- CLI v2 mode and format contract.
- Standard library registry and AST annotations.

### Changed

- Error reporting contract for human and JSON outputs.
- Preprocessor pass ordering and iterative traversal.
- Zig backend code generation coverage.

## 0.2.0

Date: November 3, 2025

- Pipeline docs output and mode contract stabilized.
- Full sample suite compiled and validated with Zig checks.
- Code generation tests expanded.

## 0.1.0

Date: November 2, 2025

- Baseline compiler with parser and semantic foundation.
- Initial set of runnable language examples.

## Update Rule

When behavior changes, update both of these files in one commit.

- `CHANGELOG.md`
- relevant page in this docs site
