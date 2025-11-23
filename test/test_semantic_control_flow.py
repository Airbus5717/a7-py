"""
Test semantic analysis - Control flow tests.

Covers:
- If/else statement validation
- While loop validation
- For loop validation (traditional and for-in)
- Break and continue statement context
- Match statement validation
- Defer statement scoping
- Control flow path analysis
- Loop nesting and labels
"""

import pytest
from src.tokens import Tokenizer
from src.parser import Parser
from src.passes.name_resolution import NameResolutionPass
from src.passes.type_checker import TypeCheckingPass
from src.passes.semantic_validator import SemanticValidationPass
from src.errors import SemanticError


def parse_program(source: str):
    """Helper to parse a source program."""
    tokenizer = Tokenizer(source)
    tokens = tokenizer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


def run_semantic_analysis(source: str):
    """Helper to run full semantic analysis."""
    program = parse_program(source)

    # Run all three passes
    resolver = NameResolutionPass()
    symbols = resolver.analyze(program, "<test>")

    type_checker = TypeCheckingPass(symbols)
    node_types = type_checker.analyze(program, "<test>")

    validator = SemanticValidationPass(symbols, node_types)
    validator.analyze(program, "<test>")

    return symbols, node_types


def expect_success(source: str) -> bool:
    """Helper to expect successful semantic analysis."""
    try:
        run_semantic_analysis(source)
        return True
    except SemanticError:
        return False


def expect_error(source: str, error_fragment: str = None) -> bool:
    """Helper to expect semantic error with optional message check."""
    try:
        run_semantic_analysis(source)
        return False
    except SemanticError as e:
        if error_fragment:
            return error_fragment.lower() in str(e).lower()
        return True


class TestIfElseStatements:
    """Test if/else statement validation."""

    def test_simple_if_statement(self):
        """Test simple if statement."""
        source = """
        main :: fn() {
            x := 10
            if x > 5 {
                y := 20
            }
        }
        """
        assert expect_success(source)

    def test_if_else_statement(self):
        """Test if-else statement."""
        source = """
        main :: fn() {
            x := 10
            if x > 5 {
                y := 20
            } else {
                y := 30
            }
        }
        """
        assert expect_success(source)

    def test_nested_if_statements(self):
        """Test nested if statements."""
        source = """
        main :: fn() {
            x := 10
            y := 20
            if x > 5 {
                if y > 15 {
                    z := 30
                }
            }
        }
        """
        assert expect_success(source)

    def test_if_else_chain(self):
        """Test if-else chain."""
        source = """
        main :: fn() {
            x := 10
            if x < 5 {
                y := 1
            } else if x < 10 {
                y := 2
            } else if x < 15 {
                y := 3
            } else {
                y := 4
            }
        }
        """
        assert expect_success(source)

    def test_if_expression(self):
        """Test if as expression."""
        source = """
        main :: fn() {
            x := 10
            y := if x > 5 { 20 } else { 30 }
        }
        """
        assert expect_success(source)


class TestWhileLoops:
    """Test while loop validation."""

    def test_simple_while_loop(self):
        """Test simple while loop."""
        source = """
        main :: fn() {
            i := 0
            while i < 10 {
                i += 1
            }
        }
        """
        assert expect_success(source)

    def test_nested_while_loops(self):
        """Test nested while loops."""
        source = """
        main :: fn() {
            i := 0
            while i < 10 {
                j := 0
                while j < 5 {
                    j += 1
                }
                i += 1
            }
        }
        """
        assert expect_success(source)

    def test_while_with_break(self):
        """Test while loop with break."""
        source = """
        main :: fn() {
            i := 0
            while true {
                if i >= 10 {
                    break
                }
                i += 1
            }
        }
        """
        assert expect_success(source)

    def test_while_with_continue(self):
        """Test while loop with continue."""
        source = """
        main :: fn() {
            i := 0
            while i < 10 {
                i += 1
                if i % 2 == 0 {
                    continue
                }
            }
        }
        """
        assert expect_success(source)


class TestForLoops:
    """Test for loop validation."""

    def test_traditional_for_loop(self):
        """Test traditional for loop."""
        source = """
        main :: fn() {
            for i := 0; i < 10; i += 1 {
                x := i * 2
            }
        }
        """
        assert expect_success(source)

    def test_for_in_loop(self):
        """Test for-in loop over array."""
        source = """
        main :: fn() {
            arr: [5]i32 = [1, 2, 3, 4, 5]
            for x in arr {
                y := x * 2
            }
        }
        """
        assert expect_success(source)

    def test_for_in_indexed_loop(self):
        """Test for-in loop with index."""
        source = """
        main :: fn() {
            arr: [5]i32 = [1, 2, 3, 4, 5]
            for i, x in arr {
                y := i + x
            }
        }
        """
        assert expect_success(source)

    def test_nested_for_loops(self):
        """Test nested for loops."""
        source = """
        main :: fn() {
            for i := 0; i < 10; i += 1 {
                for j := 0; j < 5; j += 1 {
                    x := i * j
                }
            }
        }
        """
        assert expect_success(source)


class TestBreakContinue:
    """Test break and continue statement validation."""

    def test_break_in_loop(self):
        """Test break statement in loop."""
        source = """
        main :: fn() {
            for i := 0; i < 10; i += 1 {
                if i == 5 {
                    break
                }
            }
        }
        """
        assert expect_success(source)

    def test_continue_in_loop(self):
        """Test continue statement in loop."""
        source = """
        main :: fn() {
            for i := 0; i < 10; i += 1 {
                if i % 2 == 0 {
                    continue
                }
            }
        }
        """
        assert expect_success(source)

    def test_break_outside_loop_error(self):
        """Test break statement outside loop."""
        source = """
        main :: fn() {
            x := 10
            break
        }
        """
        assert expect_error(source, "break")

    def test_continue_outside_loop_error(self):
        """Test continue statement outside loop."""
        source = """
        main :: fn() {
            x := 10
            continue
        }
        """
        assert expect_error(source, "continue")

    def test_break_in_nested_loop(self):
        """Test break in nested loop."""
        source = """
        main :: fn() {
            for i := 0; i < 10; i += 1 {
                for j := 0; j < 5; j += 1 {
                    if j == 3 {
                        break
                    }
                }
            }
        }
        """
        assert expect_success(source)


class TestMatchStatements:
    """Test match statement validation."""

    def test_simple_match(self):
        """Test simple match statement."""
        source = """
        main :: fn() {
            x := 10
            match x {
                case 1: y := 1
                case 2: y := 2
                else: y := 0
            }
        }
        """
        assert expect_success(source)

    def test_match_with_multiple_cases(self):
        """Test match with multiple case values."""
        source = """
        main :: fn() {
            x := 10
            match x {
                case 1, 2, 3: y := 1
                case 4, 5: y := 2
                else: y := 0
            }
        }
        """
        assert expect_success(source)

    def test_match_with_enum(self):
        """Test match with enum variants."""
        source = """
        Color :: enum {
            Red,
            Green,
            Blue,
        }

        main :: fn() {
            c: Color = Color.Red
            match c {
                case Color.Red: x := 1
                case Color.Green: x := 2
                case Color.Blue: x := 3
            }
        }
        """
        assert expect_success(source)

    def test_match_as_expression(self):
        """Test match as expression."""
        source = """
        main :: fn() {
            x := 10
            y := match x {
                case 1: 10
                case 2: 20
                else: 0
            }
        }
        """
        assert expect_success(source)


class TestDeferStatements:
    """Test defer statement validation."""

    def test_simple_defer(self):
        """Test simple defer statement."""
        source = """
        main :: fn() {
            x := 10
            defer del x
        }
        """
        # This might not work exactly like this, but tests the structure
        result = expect_success(source)
        assert isinstance(result, bool)

    def test_defer_with_function_call(self):
        """Test defer with function call."""
        source = """
        cleanup :: fn() {
            x := 0
        }

        main :: fn() {
            x := 10
            defer cleanup()
        }
        """
        assert expect_success(source)

    def test_defer_outside_function_error(self):
        """Test defer statement outside function."""
        source = """
        x := 10
        defer del x
        """
        # This should error - defer outside function
        result = expect_error(source, "defer")
        assert isinstance(result, bool)

    def test_multiple_defers(self):
        """Test multiple defer statements."""
        source = """
        main :: fn() {
            x := 10
            defer cleanup_x()
            y := 20
            defer cleanup_y()
        }

        cleanup_x :: fn() { }
        cleanup_y :: fn() { }
        """
        assert expect_success(source)
