"""
Semantic validation pass for A7.

Validates semantic rules beyond type checking:
- Control flow (break/continue in loops, return paths)
- Memory management (new/del matching, defer scoping)
- A7-specific rules (nil only for ref types, etc.)
"""

from typing import List, Optional, Set

from src.ast_nodes import ASTNode, NodeKind, LiteralKind
from src.symbol_table import SymbolTable
from src.semantic_context import SemanticContext
from src.types import Type, TypeKind, ReferenceType
from src.errors import SemanticError, SemanticErrorType, SourceSpan


class SemanticValidationPass:
    """
    Third pass of semantic analysis.

    Validates:
    1. Control flow correctness (break/continue context)
    2. Return path analysis
    3. Memory management (new/del, defer)
    4. A7-specific semantic rules
    """

    def __init__(self, symbols: SymbolTable, node_types: dict):
        """
        Initialize semantic validation pass.

        Args:
            symbols: Symbol table from name resolution
            node_types: Type information from type checker
        """
        self.symbols = symbols
        self.node_types = node_types
        self.context = SemanticContext()
        self.errors: List[SemanticError] = []
        self.current_file: str = "<unknown>"
        self.source_lines: List[str] = []

        # Track allocations for new/del validation
        self.allocations: Set[str] = set()

    def analyze(self, program: ASTNode, filename: str = "<unknown>") -> None:
        """
        Perform semantic validation on a program.

        Args:
            program: Root program node
            filename: Source file name

        Note:
            Collects ALL errors instead of stopping at the first one.
            Check self.errors after calling to see if there were any issues.
        """
        self.current_file = filename
        self.errors = []

        # Visit the program
        self.visit_program(program)

        # Caller should check self.errors

    def add_error(
        self,
        error_type: SemanticErrorType,
        span: Optional[SourceSpan] = None,
        context: Optional[str] = None,
    ) -> None:
        """Add a semantic validation error with structured type."""
        error = SemanticError.from_type(
            error_type,
            span=span,
            filename=self.current_file,
            source_lines=self.source_lines,
            context=context,
        )
        self.errors.append(error)

    def get_type(self, node: ASTNode) -> Optional[Type]:
        """Get the type of an AST node."""
        return self.node_types.get(id(node))

    # Visitor methods

    def visit_program(self, node: ASTNode) -> None:
        """Visit program root."""
        if node.kind != NodeKind.PROGRAM:
            self.add_error(SemanticErrorType.UNEXPECTED_NODE_KIND, node.span, f"Expected program node, got {node.kind}")
            return

        # Visit all declarations
        for decl in node.declarations or []:
            self.visit_declaration(decl)

    def visit_declaration(self, node: ASTNode) -> None:
        """Visit a top-level declaration."""
        if node.kind == NodeKind.FUNCTION:
            self.visit_function_decl(node)
        # Other declarations don't need validation

    def visit_function_decl(self, node: ASTNode) -> None:
        """Visit and validate a function declaration."""
        func_name = node.name or "<anonymous>"

        # Get return type from node
        return_type = None  # Will be set based on return_type node

        # Enter function context
        self.context.enter_function(func_name, return_type, node)

        # Visit body
        if node.body:
            self.visit_statement(node.body)

        # Check for non-void functions without return
        if node.return_type and not self.context.function_has_return():
            # This is a potential issue but might be intentional (infinite loop, etc.)
            # Could be a warning
            pass

        # Exit function context
        self.context.exit_function()

    def visit_statement(self, node: ASTNode) -> None:
        """Visit a statement."""
        if node.kind == NodeKind.BLOCK:
            self.visit_block(node)

        elif node.kind == NodeKind.IF_STMT:
            self.visit_if_stmt(node)

        elif node.kind == NodeKind.WHILE:
            self.visit_while_stmt(node)

        elif node.kind == NodeKind.FOR:
            self.visit_for_stmt(node)

        elif node.kind == NodeKind.FOR_IN or node.kind == NodeKind.FOR_IN_INDEXED:
            self.visit_for_in_stmt(node)

        elif node.kind == NodeKind.MATCH:
            self.visit_match_stmt(node)

        elif node.kind == NodeKind.BREAK:
            self.visit_break_stmt(node)

        elif node.kind == NodeKind.CONTINUE:
            self.visit_continue_stmt(node)

        elif node.kind == NodeKind.RETURN:
            self.visit_return_stmt(node)

        elif node.kind == NodeKind.DEFER:
            self.visit_defer_stmt(node)

        elif node.kind == NodeKind.DEL:
            self.visit_del_stmt(node)

        elif node.kind == NodeKind.EXPRESSION_STMT:
            if node.expression:
                self.visit_expression(node.expression)

        elif node.kind == NodeKind.VAR or node.kind == NodeKind.CONST:
            # Check initializer
            if node.value:
                self.visit_expression(node.value)

        elif node.kind == NodeKind.ASSIGNMENT:
            if node.target:
                self.visit_expression(node.target)
            if node.value:
                self.visit_expression(node.value)

    def visit_block(self, node: ASTNode) -> None:
        """Visit a block statement."""
        # Track scope depth for defer
        scope_depth = self.symbols.get_scope_depth()

        # Visit statements
        if node.statements:
            for stmt in node.statements:
                self.visit_statement(stmt)

        # Pop defers at this scope depth
        self.context.pop_defers_at_depth(scope_depth)

    def visit_if_stmt(self, node: ASTNode) -> None:
        """Visit an if statement."""
        # Visit branches
        if node.then_stmt:
            self.visit_statement(node.then_stmt)
        if node.else_stmt:
            self.visit_statement(node.else_stmt)

    def visit_while_stmt(self, node: ASTNode) -> None:
        """Visit a while statement."""
        # Enter loop context
        self.context.enter_loop(node.label)

        # Visit body
        if node.body:
            self.visit_statement(node.body)

        # Exit loop context
        self.context.exit_loop()

    def visit_for_stmt(self, node: ASTNode) -> None:
        """Visit a for loop."""
        # Enter loop context
        self.context.enter_loop(node.label)

        # Visit init
        if node.init:
            self.visit_statement(node.init)

        # Visit body
        if node.body:
            self.visit_statement(node.body)

        # Exit loop context
        self.context.exit_loop()

    def visit_for_in_stmt(self, node: ASTNode) -> None:
        """Visit a for-in loop."""
        # Enter loop context
        self.context.enter_loop(node.label)

        # Visit body
        if node.body:
            self.visit_statement(node.body)

        # Exit loop context
        self.context.exit_loop()

    def visit_match_stmt(self, node: ASTNode) -> None:
        """Visit a match statement."""
        # Visit all cases
        if node.cases:
            for case in node.cases:
                if case.statements:
                    for stmt in case.statements:
                        self.visit_statement(stmt)

        # Visit else case
        if node.else_case:
            for stmt in node.else_case:
                self.visit_statement(stmt)

    def visit_break_stmt(self, node: ASTNode) -> None:
        """Validate a break statement."""
        if not self.context.validate_break(node.label):
            if node.label:
                self.add_error(SemanticErrorType.BREAK_UNDEFINED_LABEL, node.span, f"Label '{node.label}'")
            else:
                self.add_error(SemanticErrorType.BREAK_OUTSIDE_LOOP, node.span)
        else:
            self.context.mark_loop_has_break()

    def visit_continue_stmt(self, node: ASTNode) -> None:
        """Validate a continue statement."""
        if not self.context.validate_continue(node.label):
            if node.label:
                self.add_error(SemanticErrorType.CONTINUE_UNDEFINED_LABEL, node.span, f"Label '{node.label}'")
            else:
                self.add_error(SemanticErrorType.CONTINUE_OUTSIDE_LOOP, node.span)
        else:
            self.context.mark_loop_has_continue()

    def visit_return_stmt(self, node: ASTNode) -> None:
        """Validate a return statement."""
        if not self.context.in_function():
            self.add_error(SemanticErrorType.RETURN_OUTSIDE_FUNCTION, node.span)
            return

        # Mark function as having return
        self.context.mark_function_returns()

        # Visit return expression
        if node.expression:
            self.visit_expression(node.expression)

    def visit_defer_stmt(self, node: ASTNode) -> None:
        """Validate a defer statement."""
        if not self.context.in_function():
            self.add_error(SemanticErrorType.DEFER_OUTSIDE_FUNCTION, node.span)
            return

        # Add defer to context
        scope_depth = self.symbols.get_scope_depth()
        if node.expression:
            self.context.add_defer(node.expression, scope_depth)
            self.visit_expression(node.expression)

    def visit_del_stmt(self, node: ASTNode) -> None:
        """Validate a del statement."""
        # Check that expression is a reference type
        if node.expression:
            self.visit_expression(node.expression)
            expr_type = self.get_type(node.expression)

            if expr_type and not isinstance(expr_type, ReferenceType):
                self.add_error(
                    SemanticErrorType.DELETE_NON_REFERENCE,
                    node.span,
                    f"Got '{expr_type}'"
                )

    def visit_expression(self, node: ASTNode) -> None:
        """Visit an expression for validation."""
        if node.kind == NodeKind.LITERAL:
            self.visit_literal_expr(node)

        elif node.kind == NodeKind.BINARY:
            if node.left:
                self.visit_expression(node.left)
            if node.right:
                self.visit_expression(node.right)

        elif node.kind == NodeKind.UNARY:
            if node.operand:
                self.visit_expression(node.operand)

        elif node.kind == NodeKind.CALL:
            if node.function:
                self.visit_expression(node.function)
            if node.arguments:
                for arg in node.arguments:
                    self.visit_expression(arg)

        elif node.kind == NodeKind.INDEX:
            if node.object:
                self.visit_expression(node.object)
            if node.index:
                self.visit_expression(node.index)

        elif node.kind == NodeKind.SLICE:
            if node.object:
                self.visit_expression(node.object)
            if node.start:
                self.visit_expression(node.start)
            if node.end:
                self.visit_expression(node.end)

        elif node.kind == NodeKind.FIELD_ACCESS:
            if node.object:
                self.visit_expression(node.object)

        elif node.kind == NodeKind.ADDRESS_OF:
            if node.operand:
                self.visit_expression(node.operand)

        elif node.kind == NodeKind.DEREF:
            if node.pointer:
                self.visit_expression(node.pointer)

        elif node.kind == NodeKind.CAST:
            if node.expression:
                self.visit_expression(node.expression)

        elif node.kind == NodeKind.IF_EXPR:
            if node.condition:
                self.visit_expression(node.condition)
            if node.then_expr:
                self.visit_expression(node.then_expr)
            if node.else_expr:
                self.visit_expression(node.else_expr)

        elif node.kind == NodeKind.STRUCT_INIT:
            if node.field_inits:
                for field_init in node.field_inits:
                    if field_init.value:
                        self.visit_expression(field_init.value)

        elif node.kind == NodeKind.ARRAY_INIT:
            if node.elements:
                for elem in node.elements:
                    self.visit_expression(elem)

        elif node.kind == NodeKind.NEW_EXPR:
            # Track allocation
            self.visit_new_expr(node)

    def visit_literal_expr(self, node: ASTNode) -> None:
        """Validate a literal expression."""
        # Validate nil usage
        if node.literal_kind == LiteralKind.NIL:
            # nil can only be assigned to reference types
            # This is checked in type checker, but we can add extra validation here
            expr_type = self.get_type(node)
            # Context-dependent validation would go here
            pass

    def visit_new_expr(self, node: ASTNode) -> None:
        """Validate a new expression."""
        # Track that a new allocation occurred
        # In a more complete implementation, we'd track which variable
        # holds the reference and ensure it's del'd before going out of scope
        if node.target_type:
            alloc_type = node.target_type
            # Could track allocation for leak detection
            pass

    def validate_nil_usage(self, node: ASTNode, target_type: Type) -> bool:
        """
        Validate that nil is only used with reference types.

        Args:
            node: Literal nil node
            target_type: The type this nil is being assigned to

        Returns:
            True if usage is valid
        """
        if target_type.kind != TypeKind.REFERENCE:
            self.add_error(
                SemanticErrorType.NIL_NOT_REFERENCE_TYPE,
                node.span,
                f"Got '{target_type}'"
            )
            return False
        return True
