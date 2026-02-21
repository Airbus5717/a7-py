---
layout: ../layouts/DocsLayout.astro
title: Topics
description: Inline examples grouped by topic.
---

This page keeps examples inline.

Each block is copied from `examples/*.a7` and trimmed for focus.

## Hello Program

File: `examples/001_hello.a7`

```odin
io :: import "std/io"

main :: fn() {
    io.println("Hello, World!")
}
```

## If And Else

File: `examples/006_if.a7`

```odin
x := 10
if x == 10 {
    io.println("x is 10")
} else {
    io.println("x is not 10")
}

result := if x > 0 { "positive" } else { "non-positive" }
io.println("x is {}", result)
```

## For Loops

File: `examples/005_for_loop.a7`

```odin
for i := 0; i < 5; i += 1 {
    io.println("i = {}", i)
}

numbers: [5]i32
numbers[0] = 10
numbers[1] = 20
numbers[2] = 30
numbers[3] = 40
numbers[4] = 50

for i, value in numbers {
    io.println("[{}] = {}", i, value)
}
```

## Arrays

File: `examples/012_arrays.a7`

```odin
numbers: [5]i32 = [10, 20, 30, 40, 50]

sum := 0
for i, value in numbers {
    io.println("numbers[{}] = {}", i, value)
    sum += value
}
```

## Structs

File: `examples/009_struct.a7`

```odin
Person :: struct {
    name: string
    age: i32
}

person := Person{name: "John", age: 30}
io.println("Person: {} ({})", person.name, person.age)
```

## Pointer Helpers

File: `examples/013_pointers.a7`

```odin
increment :: fn(p: ref i32) {
    p.val += 1
}

x: i32
x = 10
p: ref i32 = x.adr
increment(p)
```

## Defer Cleanup

File: `examples/024_defer.a7`

```odin
defer io.println("cleanup step 1")
defer io.println("cleanup step 2")

io.println("doing work")
```

## Generic Function

File: `examples/014_generics.a7`

```odin
main :: fn() {
    io.println("=== Generics ===")
    io.println("Generic features are demonstrated in parser and semantic tests.")
}
```

## Modules

File: `examples/018_modules.a7`

```odin
io :: import "std/io"
math :: import "std/math"

x := 9.0
io.println("sqrt({}) = {}", x, math.sqrt(x))
```

## Callback Style Dispatch

File: `examples/027_callbacks.a7`

```odin
EventType :: enum {
    Click
    Submit
    Cancel
}

handle_event :: fn(event_type: EventType) {
    match event_type {
        case EventType.Click: { io.println("click handler") }
        case EventType.Submit: { io.println("submit handler") }
        case EventType.Cancel: { io.println("cancel handler") }
    }
}
```

## Matrix Values

File: `examples/035_matrix.a7`

```odin
a: [4]f64 = [1.0, 2.0, 3.0, 4.0]
b: [4]f64 = [5.0, 6.0, 7.0, 8.0]
c: [4]f64 = [0.0, 0.0, 0.0, 0.0]

for i := 0; i < 4; i += 1 {
    c[i] = a[i] + b[i]
}
```
