# A7 Semantic Analysis TODO List

Detailed task breakdown for implementing the semantic analysis system.

**Current Phase**: Phase 1 - Module System & Symbol Resolution
**Current Status**: 98/228 semantic tests passing (43%)

---

## Phase 1: Module System & Symbol Resolution 🎯

### Task 1.1: Create Module System Infrastructure ⚡ PRIORITY

**Status**: Not Started
**Files**: `src/module_resolver.py` (exists but incomplete)

#### Subtasks:
- [ ] Design module symbol table structure
  - Module name → symbol table mapping
  - Built-in modules vs. imported modules
  - Module-qualified name resolution

- [ ] Implement `BuiltinModule` class
  - Represents standard library modules
  - Contains function/type definitions
  - Provides symbol lookup interface

- [ ] Create standard library modules
  - [ ] `io` module
    - `println(format: string, args: ..)` function
    - `print(format: string, args: ..)` function
    - `read_line() string` function
  - [ ] `math` module (future)
    - `sqrt(x: f64) f64`
    - `pow(base: f64, exp: f64) f64`
    - Constants: `PI`, `E`

- [ ] Integrate with `ModuleResolver`
  - Register built-in modules
  - Resolve module imports
  - Handle `using import` statements

#### Test Cases:
```a7
// Should resolve io.println
io.println("Hello")

// Should resolve with import
import "io"
io.println("Hello")

// Should resolve with using import
using import "io"
println("Hello")
```

#### Success Criteria:
- ✅ `io.println` resolves to built-in function
- ✅ Examples 001-007 no longer have "Undefined type (Identifier 'io')" errors
- ✅ Module-qualified access works (`module.function`)

---

### Task 1.2: Fix Symbol Table Parameter Registration ⚡ PRIORITY

**Status**: Not Started
**Files**: `src/passes/name_resolution.py`, `src/symbol_table.py`

#### Root Cause Analysis:
Function parameters are parsed correctly but not added to the symbol table when entering function scope.

#### Subtasks:
- [ ] Debug `visit_function_decl` in name resolution
  - Add logging to track parameter registration
  - Verify `define_symbol()` is called for each parameter
  - Check scope is entered before parameters defined

- [ ] Fix parameter registration
  - Ensure parameters added after entering function scope
  - Verify parameter type is resolved
  - Handle generic parameters (`$T`)

- [ ] Test parameter lookup
  - Parameters accessible in function body
  - Parameter types propagate correctly
  - Nested scopes can access outer parameters

#### Example Debug Code:
```python
def visit_function_decl(self, node: ASTNode):
    func_name = node.name or "<anonymous>"

    # Enter function scope
    self.symbols.enter_scope()

    # DEBUG: Log parameter registration
    print(f"Registering parameters for {func_name}")
    if node.parameters:
        for param in node.parameters:
            param_name = param.name
            print(f"  Defining parameter: {param_name}")
            self.symbols.define_symbol(param_name, SymbolKind.PARAMETER, param.param_type)

    # Visit body
    if node.body:
        self.visit_statement(node.body)

    self.symbols.exit_scope()
```

#### Test Cases:
```a7
add :: fn(x: i32, y: i32) i32 {
    ret x + y  // x and y should be found
}
```

#### Success Criteria:
- ✅ Function parameters found in function body
- ✅ Parameter types resolved correctly
- ✅ Error "Undefined type (Identifier 'x')" no longer appears for parameters

---

### Task 1.3: Fix Loop Variable Registration ⚡ PRIORITY

**Status**: Not Started
**Files**: `src/passes/name_resolution.py`

#### Root Cause Analysis:
Loop iteration variables not registered in symbol table:
- `for i := 0; i < 10; i += 1` - `i` not defined
- `for i in array` - `i` not defined
- `for i, elem in array` - `i` and `elem` not defined

#### Subtasks:
- [ ] Fix C-style for loop variable
  - Register init variable (`i := 0`)
  - Add to loop scope
  - Visible in condition, update, and body

- [ ] Fix for-in loop variable
  - Register iteration variable (`i in arr`)
  - Infer type from array element type
  - Add to loop scope

- [ ] Fix for-in indexed loop variables
  - Register index variable (`i`)
  - Register element variable (`elem`)
  - Infer correct types
  - Add to loop scope

#### Implementation Notes:
```python
def visit_for_stmt(self, node: ASTNode):
    # Enter loop scope
    self.symbols.enter_scope()

    # Register init variable if present
    if node.init and node.init.kind == NodeKind.VAR:
        var_name = node.init.name
        var_type = self.infer_type(node.init.value)  # May need type inference
        self.symbols.define_symbol(var_name, SymbolKind.VARIABLE, var_type)

    # Visit body
    if node.body:
        self.visit_statement(node.body)

    self.symbols.exit_scope()

def visit_for_in_stmt(self, node: ASTNode):
    # Enter loop scope
    self.symbols.enter_scope()

    # Register loop variables
    if node.kind == NodeKind.FOR_IN_INDEXED:
        # for i, elem in array
        index_name = node.index_var
        elem_name = node.element_var
        self.symbols.define_symbol(index_name, SymbolKind.VARIABLE, IntType(32))
        # elem type inferred from array element type
        self.symbols.define_symbol(elem_name, SymbolKind.VARIABLE, elem_type)
    else:
        # for elem in array
        elem_name = node.element_var
        self.symbols.define_symbol(elem_name, SymbolKind.VARIABLE, elem_type)

    # Visit body
    if node.body:
        self.visit_statement(node.body)

    self.symbols.exit_scope()
```

#### Test Cases:
```a7
// C-style for
for i := 0; i < 10; i += 1 {
    io.println("{}", i)  // i should be found
}

// for-in
arr := [1, 2, 3]
for elem in arr {
    io.println("{}", elem)  // elem should be found
}

// for-in indexed
for i, elem in arr {
    io.println("{}: {}", i, elem)  // both should be found
}
```

#### Success Criteria:
- ✅ Loop variables found in loop body
- ✅ Loop variables have correct types
- ✅ Error "Undefined type (Identifier 'i')" no longer appears in loops

---

### Task 1.4: Fix Local Variable Registration

**Status**: Not Started
**Files**: `src/passes/name_resolution.py`

#### Root Cause Analysis:
Local variables declared with `:=` or `: type =` may not be getting registered.

#### Subtasks:
- [ ] Debug `visit_var_decl`
  - Verify `define_symbol()` is called
  - Check variable is added to current scope
  - Log symbol table state

- [ ] Fix variable declaration registration
  - Handle `:=` declarations (type inference)
  - Handle `: type =` declarations (explicit type)
  - Handle uninitialized variables (`: type`)

- [ ] Verify scope visibility
  - Variables visible in subsequent statements
  - Block scopes work correctly
  - Shadowing works in nested scopes

#### Test Cases:
```a7
main :: fn() {
    count := 0  // Should be registered
    count += 5  // Should find 'count'

    {
        inner := 10  // Should be in nested scope
        count += inner  // Should find both
    }

    // inner not visible here
}
```

#### Success Criteria:
- ✅ Local variables found after declaration
- ✅ Block scopes work correctly
- ✅ Variable shadowing works (if enabled)

---

### Task 1.5: Module-Qualified Name Resolution

**Status**: Not Started
**Files**: `src/passes/name_resolution.py`, `src/passes/type_checker.py`

#### Current Issue:
`io.println` is treated as field access on undefined identifier `io`, not module-qualified function access.

#### Subtasks:
- [ ] Detect module-qualified access pattern
  - Distinguish `module.function` from `struct.field`
  - Check if left side is a module name
  - Resolve function from module symbol table

- [ ] Update name resolution
  - When seeing `FIELD_ACCESS`, check if object is module
  - If module, resolve from module's symbol table
  - Store resolved symbol reference

- [ ] Update type checker
  - Module-qualified functions have correct type
  - Function calls on module functions work
  - Arguments type check correctly

#### Implementation Notes:
```python
def visit_field_access(self, node: ASTNode):
    obj_name = node.object.name if hasattr(node.object, 'name') else None
    field_name = node.field

    # Check if this is module-qualified access
    if obj_name and self.modules.is_module(obj_name):
        # Resolve from module
        module = self.modules.get_module(obj_name)
        symbol = module.lookup(field_name)
        if symbol:
            # Store resolved symbol
            self.resolved_symbols[id(node)] = symbol
        else:
            self.add_error(
                SemanticErrorType.UNDEFINED_IN_MODULE,
                node.span,
                f"Module '{obj_name}' has no member '{field_name}'"
            )
    else:
        # Regular field access - handle normally
        ...
```

#### Test Cases:
```a7
// Module-qualified access
io.println("Hello")  // Should resolve to io module's println function

// With import
import "io"
io.println("World")

// With using import
using import "io"
println("Direct")  // Should also work
```

#### Success Criteria:
- ✅ `io.println` resolves as module function, not field access
- ✅ Module functions callable
- ✅ Errors specific to module resolution (not "field access on non-struct")

---

### Phase 1 Testing & Validation

**Test Files**: Examples 001-007

- [ ] 001_hello.a7 - Basic module usage
- [ ] 002_var.a7 - Variables and constants
- [ ] 004_func.a7 - Functions with parameters
- [ ] 005_for_loop.a7 - Loop variables
- [ ] 006_if.a7 - Control flow with variables
- [ ] 007_while.a7 - While loops with variables

**Success Criteria for Phase 1**:
- ✅ All 6 test files compile without symbol resolution errors
- ✅ Error count reduced from ~3,300 to ~1,300 (60% reduction)
- ✅ `io.println` works in all examples
- ✅ Function parameters accessible
- ✅ Loop variables accessible
- ✅ Local variables tracked

---

## Phase 2: Type Inference & Propagation 🔍

### Task 2.1: Basic Type Inference from Literals

**Status**: Not Started
**Files**: `src/passes/type_checker.py`

#### Subtasks:
- [ ] Implement literal type inference
  - Integer literals → `i32` (default) or infer from context
  - Float literals → `f64` (default) or infer from context
  - String literals → `string`
  - Bool literals → `bool`
  - Array literals → `[N]T` where T is element type

- [ ] Implement variable declaration inference
  - `x := 42` → infer `i32` for `x`
  - `name := "Alice"` → infer `string` for `name`
  - `arr := [1, 2, 3]` → infer `[3]i32` for `arr`

- [ ] Store inferred types in symbol table
  - Update symbol's type after inference
  - Make type available for subsequent uses

#### Implementation Notes:
```python
def visit_var_decl(self, node: ASTNode):
    var_name = node.name

    if node.value:
        # Infer type from initializer
        init_type = self.infer_expression_type(node.value)

        if node.var_type:
            # Explicit type - verify compatibility
            declared_type = self.resolve_type(node.var_type)
            if not self.types_compatible(declared_type, init_type):
                self.add_error(...)
            var_type = declared_type
        else:
            # Type inference
            var_type = init_type

        # Store type in symbol table
        symbol = self.symbols.lookup(var_name)
        if symbol:
            symbol.type = var_type

        # Store in node_types for AST
        self.node_types[id(node)] = var_type
```

#### Test Cases:
```a7
x := 42          // Infer i32
pi := 3.14159    // Infer f64
name := "Alice"  // Infer string
active := true   // Infer bool
arr := [1, 2, 3] // Infer [3]i32
```

#### Success Criteria:
- ✅ Variables have concrete types, not `unknown type`
- ✅ Subsequent uses of variable have correct type
- ✅ Type inference works for all literal types

---

### Task 2.2: Expression Type Inference

**Status**: Not Started
**Files**: `src/passes/type_checker.py`

#### Subtasks:
- [ ] Binary operation type inference
  - Arithmetic: `i32 + i32 → i32`, `f64 * f64 → f64`
  - Comparison: `i32 < i32 → bool`
  - Logical: `bool and bool → bool`
  - Bitwise: `i32 & i32 → i32`

- [ ] Unary operation type inference
  - Negation: `-i32 → i32`
  - Logical not: `not bool → bool`
  - Bitwise not: `~i32 → i32`

- [ ] Function call type inference
  - `add(1, 2)` → return type of `add`
  - Generic function instantiation
  - Method call return types

- [ ] Compound expressions
  - `x := a + b * c` → infer from subexpressions
  - Operator precedence handling
  - Type promotion rules

#### Test Cases:
```a7
sum := 5 + 7              // i32
product := 2.5 * 3.0      // f64
is_equal := x == y        // bool
result := add(10, 20)     // i32 (from function return type)
```

#### Success Criteria:
- ✅ All expressions have concrete types
- ✅ Binary/unary operations infer correctly
- ✅ Function calls infer return types

---

### Task 2.3: Type Propagation Through Assignments

**Status**: Not Started
**Files**: `src/passes/type_checker.py`

#### Current Issue:
Compound assignments fail because target has `unknown type`.

#### Subtasks:
- [ ] Fix assignment type checking
  - Look up variable's current type
  - Verify assignment value compatible
  - Update type if needed (for inference)

- [ ] Fix compound assignments
  - `count += 5` → get type of `count`, verify `i32 + i32`
  - `value *= 2` → get type of `value`, verify numeric
  - All compound operators: `+=`, `-=`, `*=`, `/=`, `%=`, `&=`, `|=`, `^=`, `<<=`, `>>=`

- [ ] Handle type promotion
  - Widening conversions (optional)
  - Narrowing conversions (error or explicit cast)

#### Test Cases:
```a7
count := 0      // Infer i32
count += 5      // Should work (i32 + i32)
count *= 2      // Should work (i32 * i32)

value := 1.0    // Infer f64
value /= 2.0    // Should work (f64 / f64)
```

#### Success Criteria:
- ✅ Compound assignments work on inferred types
- ✅ No "expected 'unknown type'" errors
- ✅ Type propagation through assignment chains

---

### Task 2.4: Array and Indexing Type Inference

**Status**: Not Started
**Files**: `src/passes/type_checker.py`

#### Subtasks:
- [ ] Array initialization type inference
  - `[1, 2, 3]` → `[3]i32`
  - `[[1, 2], [3, 4]]` → `[2][2]i32`
  - Verify all elements same type

- [ ] Array indexing result type
  - `arr[0]` → element type of `arr`
  - Multi-dimensional indexing
  - Slice indexing

- [ ] Slice type inference
  - `arr[1:3]` → slice type
  - Dynamic array handling

#### Test Cases:
```a7
nums := [1, 2, 3]        // [3]i32
first := nums[0]         // i32
matrix := [[1,2],[3,4]]  // [2][2]i32
row := matrix[0]         // [2]i32
elem := matrix[0][1]     // i32
```

#### Success Criteria:
- ✅ Array types inferred from elements
- ✅ Indexing returns element type
- ✅ Multi-dimensional arrays work
- ✅ No "Cannot index this type: got 'unknown type'" errors

---

### Task 2.5: Generic Type Instantiation

**Status**: Not Started
**Files**: `src/passes/type_checker.py`, `src/generics.py`

#### Subtasks:
- [ ] Generic function instantiation
  - Infer generic parameters from arguments
  - `swap(x, y)` → instantiate `$T` from types of `x` and `y`
  - Create monomorphized version

- [ ] Generic struct instantiation
  - `List(i32){...}` → instantiate `$T` with `i32`
  - Verify type arguments match constraints

- [ ] Type constraint checking
  - `$T: Numeric` → verify `T` satisfies constraint
  - Type sets: `$T: @type_set(i32, i64)`

#### Test Cases:
```a7
swap :: fn($T, a: ref T, b: ref T) {
    temp := a.val
    a.val = b.val
    b.val = temp
}

x := 5
y := 10
swap(x.adr, y.adr)  // Infer T = i32
```

#### Success Criteria:
- ✅ Generic functions instantiate automatically
- ✅ Type constraints validated
- ✅ Generic structs work with explicit instantiation

---

### Phase 2 Testing & Validation

**Test Files**: Examples 008-015

- [ ] 009_struct.a7 - Struct field types
- [ ] 011_memory.a7 - Memory operations with inference
- [ ] 012_arrays.a7 - Array type inference
- [ ] 013_pointers.a7 - Pointer type inference
- [ ] 014_generics.a7 - Generic instantiation

**Success Criteria for Phase 2**:
- ✅ Error count reduced from ~1,300 to ~650 (50% reduction)
- ✅ Type inference working for variables
- ✅ Compound assignments work
- ✅ Array operations type check
- ✅ Generic functions instantiate

---

## Phase 3: Return Types & Control Flow 🔄

### Task 3.1: Return Expression Type Evaluation

**Status**: Not Started
**Files**: `src/passes/type_checker.py`

#### Current Issue:
All return statements show `got 'None'` instead of actual return type.

#### Subtasks:
- [ ] Evaluate return expression before type check
  - Compute expression type
  - Store in node_types
  - Compare with function return type

- [ ] Handle void returns
  - Functions without return type
  - Return without expression
  - Implicit return at end

- [ ] Return type validation
  - Verify return type matches declaration
  - Handle multiple return statements
  - Track return types through paths

#### Implementation Fix:
```python
def visit_return_stmt(self, node: ASTNode):
    if not self.context.in_function():
        self.add_type_error(...)
        return

    func_return_type = self.context.current_function_return_type()

    if node.expression:
        # EVALUATE the expression type FIRST
        return_type = self.visit_expression(node.expression)

        # NOW compare with expected type
        if func_return_type and not self.types_compatible(func_return_type, return_type):
            self.add_type_error(
                TypeErrorType.RETURN_TYPE_MISMATCH,
                node.span,
                f"expected '{func_return_type}', got '{return_type}'"
            )
    else:
        # No expression - should be void function
        if func_return_type and func_return_type.kind != TypeKind.VOID:
            self.add_type_error(...)
```

#### Test Cases:
```a7
add :: fn(x: i32, y: i32) i32 {
    ret x + y  // Should verify i32 == i32
}

greet :: fn(name: string) {
    io.println("Hello, {}", name)
    // Void return - ok to have no return statement
}

max :: fn(a: i32, b: i32) i32 {
    if a > b {
        ret a  // i32
    }
    ret b  // i32
}
```

#### Success Criteria:
- ✅ Return types evaluated correctly
- ✅ No "got 'None'" errors
- ✅ Type mismatches show actual types

---

### Task 3.2: Control Flow Return Path Analysis

**Status**: Not Started
**Files**: `src/passes/semantic_validator.py`

#### Subtasks:
- [ ] Track whether function returns on all paths
  - If/else both paths return
  - Match statement all cases return
  - Early returns

- [ ] Warn on missing returns
  - Non-void function without return
  - Unreachable code after return

- [ ] Handle early returns
  - Return in if statement
  - Multiple returns in function

#### Test Cases:
```a7
// Should warn - missing return
bad :: fn() i32 {
    x := 5
    // No return!
}

// Should be ok - both paths return
good :: fn(x: i32) i32 {
    if x > 0 {
        ret x
    }
    ret -x
}
```

#### Success Criteria:
- ✅ Missing return warnings
- ✅ All paths checked
- ✅ Early returns handled

---

### Phase 3 Testing & Validation

**Test Files**: Examples 004, 021, 022

- [ ] 004_func.a7 - Function return types
- [ ] 021_control_flow.a7 - Control flow return paths
- [ ] 022_function_pointers.a7 - Function pointer returns

**Success Criteria for Phase 3**:
- ✅ Error count reduced by ~240
- ✅ Return type checking works
- ✅ All paths validated

---

## Phase 4: Enum & Union Support 🏷️

### Task 4.1: Enum Variant Resolution

**Status**: Not Started
**Files**: `src/passes/type_checker.py`

#### Subtasks:
- [ ] Detect enum variant access
  - `Color.Red` → check if `Color` is enum
  - Verify variant exists
  - Type as enum type, not field access

- [ ] Pattern matching on enums
  - Match cases validate variant names
  - Exhaustiveness checking

#### Test Cases:
```a7
Color :: enum {
    Red
    Green
    Blue
}

c := Color.Red  // Should work
```

#### Success Criteria:
- ✅ Enum variant access works
- ✅ No "cannot access field" errors on enums

---

### Task 4.2: Union Tag Access

**Status**: Not Started
**Files**: `src/passes/type_checker.py`

#### Subtasks:
- [ ] Union tag field access
  - Access tag field
  - Validate tag-based access

#### Success Criteria:
- ✅ Union tag access works

---

### Phase 4 Testing

**Test Files**: Examples 010, 016

- [ ] 010_enum.a7 - Enum variants
- [ ] 016_unions.a7 - Union tags

**Success Criteria for Phase 4**:
- ✅ Enum examples compile
- ✅ Union examples compile

---

## Phase 5: Pointer & Reference Operations 👉

### Task 5.1: Pointer Operation Type Checking

**Status**: Not Started
**Files**: `src/passes/type_checker.py`

#### Subtasks:
- [ ] `.adr` operation
  - Check operand is lvalue
  - Result type is `ptr T`

- [ ] `.val` operation
  - Check operand is pointer
  - Result type is `T`

#### Test Cases:
```a7
x := 42
ptr := x.adr  // ptr i32
value := ptr.val  // i32
```

#### Success Criteria:
- ✅ Pointer operations type check
- ✅ No "requires pointer type: got 'unknown type'" errors

---

### Phase 5 Testing

**Test Files**: Examples 011, 013, 024

- [ ] 011_memory.a7 - Memory management
- [ ] 013_pointers.a7 - Pointer operations
- [ ] 024_defer.a7 - Defer with pointers

---

## Phase 6: Advanced Features 🚀

### Task 6.1: Method Resolution

**Status**: Not Started

#### Subtasks:
- [ ] Method call resolution
- [ ] `self` parameter typing
- [ ] Method dispatch

#### Test Files:
- [ ] 017_methods.a7

---

### Task 6.2: Function Pointers

**Status**: Not Started

#### Subtasks:
- [ ] Function pointer types
- [ ] Function pointer calls
- [ ] Callbacks

#### Test Files:
- [ ] 022_function_pointers.a7
- [ ] 027_callbacks.a7

---

### Task 6.3: Complex Data Structures

**Status**: Not Started

#### Test Files:
- [ ] 025_linked_list.a7
- [ ] 026_binary_tree.a7
- [ ] 028_state_machine.a7
- [ ] 029_sorting.a7

---

## Phase 7: Polish & Edge Cases ✨

### Task 7.1: Variable Shadowing

**Status**: Not Started
**Files**: `src/symbol_table.py`

#### Subtasks:
- [ ] Allow shadowing in nested scopes
- [ ] Prevent redefinition in same scope

#### Test Files:
- [ ] 032_prime_numbers.a7

---

### Task 7.2: Remaining Examples

**Status**: Not Started

#### Test Files:
- [ ] 030_calculator.a7
- [ ] 031_number_guessing.a7
- [ ] 033_fibonacci.a7
- [ ] 034_string_utils.a7
- [ ] 035_matrix.a7

---

## Progress Tracking

### Overall Progress
- [ ] Phase 1: Module System & Symbol Resolution (0%)
- [ ] Phase 2: Type Inference & Propagation (0%)
- [ ] Phase 3: Return Types & Control Flow (0%)
- [ ] Phase 4: Enum & Union Support (0%)
- [ ] Phase 5: Pointer & Reference Operations (0%)
- [ ] Phase 6: Advanced Features (0%)
- [ ] Phase 7: Polish & Edge Cases (0%)

### Error Reduction Goals
- Current: ~3,300 errors across 31 files
- Phase 1 target: ~1,300 errors (60% reduction)
- Phase 2 target: ~650 errors (50% reduction from P1)
- Phase 3 target: ~410 errors (37% reduction from P2)
- Final target: 0 errors (100% reduction)

### Test Coverage Goals
- Current: 98/228 semantic tests passing (43%)
- Phase 1 target: ~140/228 passing (61%)
- Phase 2 target: ~180/228 passing (79%)
- Phase 3 target: ~210/228 passing (92%)
- Final target: 228/228 passing (100%)

---

## Quick Start: Next Immediate Actions

**Start with Task 1.1** - Create module system:

1. Open `src/module_resolver.py`
2. Create `BuiltinModule` class
3. Add `io` module with `println` function
4. Integrate with compilation pipeline
5. Test with `examples/001_hello.a7`

See `PHASES.md` for high-level roadmap and timeline.
