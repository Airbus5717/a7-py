---
layout: ../layouts/DocsLayout.astro
title: Language
description: Core language rules with practical examples.
---

## Declarations

Use `::` for named declarations.

```odin
sum :: fn(a: i32, b: i32) i32 {
    ret a + b
}
```

Use `:=` for local inference.

```odin
count := 42
name := "a7"
```

## Type System

Primitive types include `i32`, `i64`, `f32`, `f64`, `bool`, `char`, and `string`.

Composite types include arrays, slices, structs, unions, and enums.

```odin
Point :: struct {
    x: f64,
    y: f64,
}

Color :: enum { Red, Green, Blue }
```

## Expressions

Expressions support literals, calls, member access, indexing, casts, and operators.

```odin
value := arr[i + 1]
flag := a > b && ready
size := cast(i64)small
```

## Control Flow

Use `if`, `else`, `while`, and `for`.

Use `match` for structured branching.

```odin
if score > 90 {
    grade := "A"
} else {
    grade := "B"
}

match event {
    .Start => println("start"),
    .Stop => println("stop"),
}
```

## Functions And Generics

Functions are first class values.

Generic parameters use `$T`.

```odin
identity :: fn($T, x: T) T {
    ret x
}
```

Type sets can constrain type arguments.

```odin
Number :: type_set { i32 | i64 | f32 | f64 }
```

## Memory Model

Use stack allocation by default.

Use `new` and `delete` for heap allocation.

Use `defer` for cleanup.

```odin
node := new Node
if node != nil {
    defer delete node
}
```

Pointer helpers `.adr` and `.val` are lowered before codegen.

## Modules

Modules map to files.

Imports support named, alias, and using forms.

```odin
import "std/io"
import "math" as m
using import "std/math"
```

## Diagnostics

Compiler errors are grouped by stage.

Use mode based debugging when triaging failures.

Use machine output in CI.

```bash
uv run python main.py --format json --mode semantic examples/014_generics.a7
```

## Limits

Labeled loops are deferred.

Advanced array programming library depth is deferred.

Alternative backends are deferred.
