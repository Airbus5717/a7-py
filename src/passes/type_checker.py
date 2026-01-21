"""
Type checking pass for A7 semantic analysis.

Performs type inference, type checking, and type compatibility validation.
"""

from typing import Optional, List, Dict

from src.ast_nodes import ASTNode, NodeKind, BinaryOp, UnaryOp, LiteralKind
from src.symbol_table import SymbolTable, Symbol, SymbolKind
from src.semantic_context import SemanticContext
from src.types import (
    Type, TypeKind,
    PrimitiveType, ArrayType, SliceType, PointerType, ReferenceType,
    FunctionType, StructType, StructField, EnumType, EnumVariant,
    UnionType, UnionField, GenericParamType, GenericInstanceType,
    TypeSet, VoidType, UnknownType,
    BOOL, CHAR, STRING, I8, I16, I32, I64, U8, U16, U32, U64, F32, F64,
    VOID, UNKNOWN, NUMERIC, INTEGER,
    get_primitive_type, get_predefined_type_set
)
from src.errors import SemanticError, TypeCheckError, TypeErrorType, SemanticErrorType, SourceSpan


class TypeCheckingPass:
    """
    Second pass of semantic analysis.

    Performs:
    1. Type inference for := declarations
    2. Type checking for all expressions
    3. Function call argument/return type validation
    4. Assignment compatibility checking
    5. Generic type constraint validation
    """

    def __init__(self, symbols: SymbolTable):
        """
        Initialize type checking pass.

        Args:
            symbols: Symbol table from name resolution pass
        """
        self.symbols = symbols
        self.context = SemanticContext()
        self.errors: List[SemanticError] = []
        self.current_file: str = "<unknown>"
        self.source_lines: List[str] = []

        # Cache for type information attached to AST nodes
        self.node_types: Dict[int, Type] = {}

    def analyze(self, program: ASTNode, filename: str = "<unknown>") -> None:
        """
        Perform type checking on a program.

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

    def add_error(self, message: str, span: Optional[SourceSpan] = None) -> None:
        """Add a type checking error (legacy - prefer add_type_error)."""
        error = SemanticError(message, span, self.current_file)
        self.errors.append(error)

    def add_type_error(
        self,
        error_type: TypeErrorType,
        span: Optional[SourceSpan] = None,
        expected_type: Optional[str] = None,
        got_type: Optional[str] = None,
        context: Optional[str] = None,
    ) -> None:
        """Add a type checking error with structured type."""
        error = TypeCheckError.from_type(
            error_type,
            span=span,
            filename=self.current_file,
            source_lines=self.source_lines,
            expected_type=expected_type,
            got_type=got_type,
            context=context,
        )
        self.errors.append(error)

    def set_type(self, node: ASTNode, type_: Type) -> None:
        """Associate a type with an AST node."""
        self.node_types[id(node)] = type_

    def get_type(self, node: ASTNode) -> Optional[Type]:
        """Get the type of an AST node."""
        return self.node_types.get(id(node))

    # Visitor methods

    def visit_program(self, node: ASTNode) -> None:
        """Visit program root."""
        if node.kind != NodeKind.PROGRAM:
            error = SemanticError.from_type(SemanticErrorType.UNEXPECTED_NODE_KIND, span=node.span, filename=self.current_file, source_lines=self.source_lines, context=f"Expected program node, got {node.kind}")
            self.errors.append(error)
            return

        # First pass: register all type declarations
        for decl in node.declarations or []:
            if decl.kind in {NodeKind.STRUCT, NodeKind.ENUM, NodeKind.UNION, NodeKind.TYPE_ALIAS}:
                self.register_type_decl(decl)

        # Second pass: type check all declarations
        for decl in node.declarations or []:
            self.visit_declaration(decl)

    def register_type_decl(self, node: ASTNode) -> None:
        """Register a type declaration (first pass)."""
        if node.kind == NodeKind.STRUCT:
            self.register_struct_type(node)
        elif node.kind == NodeKind.ENUM:
            self.register_enum_type(node)
        elif node.kind == NodeKind.UNION:
            self.register_union_type(node)
        # TYPE_ALIAS will be resolved on-demand

    def register_struct_type(self, node: ASTNode) -> None:
        """Register a struct type."""
        struct_name = node.name or "<anonymous>"

        # Create struct fields (types will be resolved lazily)
        fields = []
        if node.fields:
            for field_node in node.fields:
                if field_node.kind == NodeKind.FIELD:
                    field_name = field_node.name or "<unknown>"
                    # Resolve field type
                    field_type = self.resolve_type_node(field_node.field_type) if field_node.field_type else UNKNOWN
                    fields.append(StructField(name=field_name, field_type=field_type))

        # Create struct type
        generic_params = tuple(gp.name for gp in (node.generic_params or []))
        struct_type = StructType(name=struct_name, fields=tuple(fields), generic_params=generic_params)

        # Update symbol
        symbol = self.symbols.lookup(struct_name)
        if symbol:
            symbol.type = struct_type

    def register_enum_type(self, node: ASTNode) -> None:
        """Register an enum type."""
        enum_name = node.name or "<anonymous>"

        # Create enum variants
        variants = []
        if node.variants:
            for variant_node in node.variants:
                if variant_node.kind == NodeKind.ENUM_VARIANT:
                    variant_name = variant_node.name or "<unknown>"
                    # Extract value if present (will be int literal)
                    value = None
                    if variant_node.value:
                        value = self.extract_int_value(variant_node.value)
                    variants.append(EnumVariant(name=variant_name, value=value))

        # Create enum type
        enum_type = EnumType(name=enum_name, variants=tuple(variants))

        # Update symbol
        symbol = self.symbols.lookup(enum_name)
        if symbol:
            symbol.type = enum_type

    def register_union_type(self, node: ASTNode) -> None:
        """Register a union type."""
        union_name = node.name or "<anonymous>"

        # Create union fields
        fields = []
        if node.fields:
            for field_node in node.fields:
                if field_node.kind == NodeKind.FIELD:
                    field_name = field_node.name or "<unknown>"
                    field_type = self.resolve_type_node(field_node.field_type) if field_node.field_type else UNKNOWN
                    fields.append(UnionField(name=field_name, field_type=field_type))

        # Create union type
        union_type = UnionType(name=union_name, fields=tuple(fields))

        # Update symbol
        symbol = self.symbols.lookup(union_name)
        if symbol:
            symbol.type = union_type

    def extract_int_value(self, node: ASTNode) -> Optional[int]:
        """Extract integer value from a literal node."""
        if node.kind == NodeKind.LITERAL and node.literal_kind == LiteralKind.INTEGER:
            return node.literal_value
        return None

    def resolve_type_node(self, node: Optional[ASTNode]) -> Type:
        """
        Resolve a type expression to a Type object.

        Args:
            node: Type expression AST node

        Returns:
            Resolved Type
        """
        if node is None:
            return UNKNOWN

        if node.kind == NodeKind.TYPE_PRIMITIVE:
            # Primitive type like i32, f64, bool
            type_name = node.type_name or ""
            prim_type = get_primitive_type(type_name)
            return prim_type if prim_type else UNKNOWN

        elif node.kind == NodeKind.TYPE_IDENTIFIER:
            # Named type (struct, enum, union, type alias)
            # Note: Parser stores type name in 'name' attribute, not 'type_name'
            type_name = node.name or node.type_name or ""
            symbol = self.symbols.lookup(type_name)
            if symbol:
                return symbol.type
            else:
                self.add_type_error(TypeErrorType.UNDEFINED_TYPE, node.span, context=f"Type '{type_name}'")
                return UNKNOWN

        elif node.kind == NodeKind.TYPE_ARRAY:
            # Fixed-size array: [N]T
            elem_type = self.resolve_type_node(node.element_type)
            size = self.extract_int_value(node.size) if node.size else 0
            return ArrayType(element_type=elem_type, size=size)

        elif node.kind == NodeKind.TYPE_SLICE:
            # Dynamic slice: []T
            elem_type = self.resolve_type_node(node.element_type)
            return SliceType(element_type=elem_type)

        elif node.kind == NodeKind.TYPE_POINTER:
            # Pointer: ptr T
            pointee_type = self.resolve_type_node(node.target_type)
            return PointerType(pointee_type=pointee_type)

        elif node.kind == NodeKind.TYPE_FUNCTION:
            # Function type: fn(params...) return_type
            param_types = []
            if node.parameter_types:
                for pt in node.parameter_types:
                    param_types.append(self.resolve_type_node(pt))

            return_type = self.resolve_type_node(node.return_type) if node.return_type else None
            is_variadic = node.is_variadic or False
            variadic_type = self.resolve_type_node(node.param_type) if node.param_type and is_variadic else None

            return FunctionType(
                param_types=tuple(param_types),
                return_type=return_type,
                is_variadic=is_variadic,
                variadic_type=variadic_type
            )

        elif node.kind == NodeKind.TYPE_STRUCT:
            # Inline/anonymous struct type
            fields = []
            if node.fields:
                for field_node in node.fields:
                    if field_node.kind == NodeKind.FIELD:
                        field_name = field_node.name or "<unknown>"
                        field_type = self.resolve_type_node(field_node.field_type) if field_node.field_type else UNKNOWN
                        fields.append(StructField(name=field_name, field_type=field_type))

            return StructType(name=None, fields=tuple(fields))

        elif node.kind == NodeKind.TYPE_GENERIC:
            # Generic instantiation: List(i32)
            base_name = node.type_name or ""
            type_args = []
            if node.type_args:
                for arg in node.type_args:
                    type_args.append(self.resolve_type_node(arg))

            return GenericInstanceType(base_name=base_name, type_args=tuple(type_args))

        elif node.kind == NodeKind.TYPE_SET:
            # Type set: @type_set(i32, i64)
            types_in_set = []
            if node.types:
                for t in node.types:
                    types_in_set.append(self.resolve_type_node(t))

            return TypeSet(types=frozenset(types_in_set))

        else:
            error = SemanticError.from_type(SemanticErrorType.UNEXPECTED_NODE_KIND, span=node.span, filename=self.current_file, source_lines=self.source_lines, context=f"Unknown type node kind: {node.kind}")
            self.errors.append(error)
            return UNKNOWN

    def visit_declaration(self, node: ASTNode) -> None:
        """Visit a top-level declaration."""
        if node.kind == NodeKind.FUNCTION:
            self.visit_function_decl(node)
        elif node.kind == NodeKind.CONST:
            self.visit_const_decl(node)
        elif node.kind == NodeKind.VAR:
            self.visit_var_decl(node)
        # Struct/enum/union already registered

    def visit_function_decl(self, node: ASTNode) -> None:
        """Visit and type check a function declaration."""
        func_name = node.name or "<anonymous>"

        # Enter function scope for parameter and body processing
        self.symbols.enter_scope(f"function_{func_name}")

        # Resolve return type
        return_type = self.resolve_type_node(node.return_type) if node.return_type else None

        # Resolve parameter types and register parameters in this scope
        param_types = []
        if node.parameters:
            for param in node.parameters:
                param_type = self.resolve_type_node(param.param_type) if param.param_type else UNKNOWN
                param_types.append(param_type)

                # Register parameter in function scope
                param_name = param.name or ""
                param_symbol = Symbol(
                    name=param_name,
                    kind=SymbolKind.VARIABLE,
                    type=param_type,
                    node=param,
                    is_mutable=False
                )
                self.symbols.define(param_symbol)

        # Check for variadic
        is_variadic = node.is_variadic or False
        variadic_type = None
        if is_variadic and node.parameters:
            last_param = node.parameters[-1]
            if last_param.param_type:
                variadic_type = self.resolve_type_node(last_param.param_type)

        # Create function type
        func_type = FunctionType(
            param_types=tuple(param_types),
            return_type=return_type,
            is_variadic=is_variadic,
            variadic_type=variadic_type
        )

        # Update function symbol (in outer scope)
        func_symbol = self.symbols.lookup(func_name)
        if func_symbol:
            func_symbol.type = func_type

        # Enter function context
        self.context.enter_function(func_name, return_type, node)

        # Type check body
        if node.body:
            self.visit_statement(node.body)

        # Check that non-void functions have return
        if return_type is not None and not self.context.function_has_return():
            # Allow functions that might not return (e.g., always infinite loop)
            # This is a warning-level issue, not an error
            pass

        # Exit function context
        self.context.exit_function()

        # Exit function scope
        self.symbols.exit_scope()

    def visit_const_decl(self, node: ASTNode) -> None:
        """Visit a constant declaration."""
        const_name = node.name or "<unknown>"

        # Type check the value
        value_type = UNKNOWN
        if node.value:
            value_type = self.visit_expression(node.value)

        # If explicit type given, check compatibility
        if node.explicit_type:
            explicit_type = self.resolve_type_node(node.explicit_type)
            if not value_type.is_assignable_to(explicit_type):
                self.add_type_error(
                    TypeErrorType.TYPE_MISMATCH,
                    node.span,
                    expected_type=str(explicit_type),
                    got_type=str(value_type),
                    context=f"Constant '{const_name}'"
                )
            value_type = explicit_type

        # Update symbol
        symbol = self.symbols.lookup(const_name)
        if symbol:
            symbol.type = value_type

    def visit_var_decl(self, node: ASTNode) -> None:
        """Visit a variable declaration."""
        var_name = node.name or "<unknown>"

        # Check for nil literal
        is_nil_value = (node.value and node.value.kind == NodeKind.LITERAL
                        and node.value.literal_kind == LiteralKind.NIL)

        # Type check the value if present
        value_type = UNKNOWN
        if node.value:
            value_type = self.visit_expression(node.value)

        # Determine final type
        if node.explicit_type:
            # Explicit type annotation
            explicit_type = self.resolve_type_node(node.explicit_type)

            # Check nil assignment to non-reference type
            if is_nil_value and not isinstance(explicit_type, ReferenceType):
                self.add_type_error(
                    TypeErrorType.NIL_ONLY_FOR_REFERENCES,
                    node.span,
                    got_type=str(explicit_type),
                    context=f"Variable '{var_name}'"
                )
            elif node.value and not is_nil_value and not value_type.is_assignable_to(explicit_type):
                self.add_type_error(
                    TypeErrorType.TYPE_MISMATCH,
                    node.span,
                    expected_type=str(explicit_type),
                    got_type=str(value_type),
                    context=f"Variable '{var_name}'"
                )
            value_type = explicit_type
        elif not node.value:
            # No value and no type - error
            error = SemanticError.from_type(SemanticErrorType.MISSING_TYPE_ANNOTATION, span=node.span, filename=self.current_file, source_lines=self.source_lines, context=f"Variable '{var_name}' requires either type annotation or initializer")
            self.errors.append(error)
            value_type = UNKNOWN

        # Register variable in current scope (type checker manages its own scopes)
        var_symbol = Symbol(
            name=var_name,
            kind=SymbolKind.VARIABLE,
            type=value_type,
            node=node,
            is_mutable=True
        )
        self.symbols.define(var_symbol)

    def visit_statement(self, node: ASTNode) -> None:
        """Visit a statement."""
        if node.kind == NodeKind.BLOCK:
            if node.statements:
                for stmt in node.statements:
                    self.visit_statement(stmt)

        elif node.kind == NodeKind.VAR:
            self.visit_var_decl(node)

        elif node.kind == NodeKind.CONST:
            self.visit_const_decl(node)

        elif node.kind == NodeKind.EXPRESSION_STMT:
            if node.expression:
                self.visit_expression(node.expression)

        elif node.kind == NodeKind.ASSIGNMENT:
            self.visit_assignment(node)

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

        elif node.kind == NodeKind.RETURN:
            self.visit_return_stmt(node)

        elif node.kind == NodeKind.BREAK:
            # Validated in semantic validator pass
            pass

        elif node.kind == NodeKind.CONTINUE:
            # Validated in semantic validator pass
            pass

        elif node.kind == NodeKind.DEFER:
            if node.expression:
                self.visit_expression(node.expression)

        elif node.kind == NodeKind.DEL:
            if node.expression:
                self.visit_expression(node.expression)

    def visit_assignment(self, node: ASTNode) -> None:
        """Visit an assignment statement."""
        # Type check both sides
        lhs_type = self.visit_expression(node.target) if node.target else UNKNOWN
        rhs_type = self.visit_expression(node.value) if node.value else UNKNOWN

        # Check assignment compatibility
        if not rhs_type.is_assignable_to(lhs_type):
            self.add_type_error(
                TypeErrorType.ASSIGNMENT_TYPE_MISMATCH,
                node.span,
                expected_type=str(lhs_type),
                got_type=str(rhs_type)
            )

    def visit_if_stmt(self, node: ASTNode) -> None:
        """Visit an if statement."""
        # Condition must be boolean
        if node.condition:
            cond_type = self.visit_expression(node.condition)
            if not cond_type.equals(BOOL):
                self.add_type_error(TypeErrorType.CONDITION_NOT_BOOL, node.condition.span, expected_type="bool", got_type=str(cond_type))

        # Visit branches
        if node.then_stmt:
            self.visit_statement(node.then_stmt)
        if node.else_stmt:
            self.visit_statement(node.else_stmt)

    def visit_while_stmt(self, node: ASTNode) -> None:
        """Visit a while statement."""
        # Condition must be boolean
        if node.condition:
            cond_type = self.visit_expression(node.condition)
            if not cond_type.equals(BOOL):
                self.add_type_error(TypeErrorType.CONDITION_NOT_BOOL, node.condition.span, expected_type="bool", got_type=str(cond_type))

        # Enter loop context
        self.context.enter_loop()

        # Visit body
        if node.body:
            self.visit_statement(node.body)

        # Exit loop context
        self.context.exit_loop()

    def visit_for_stmt(self, node: ASTNode) -> None:
        """Visit a for loop."""
        # Enter loop context
        self.context.enter_loop()

        # Type check init, condition, update
        if node.init:
            self.visit_statement(node.init)

        if node.condition:
            cond_type = self.visit_expression(node.condition)
            if not cond_type.equals(BOOL):
                self.add_type_error(TypeErrorType.CONDITION_NOT_BOOL, node.condition.span, expected_type="bool", got_type=str(cond_type))

        if node.update:
            self.visit_statement(node.update)

        # Visit body
        if node.body:
            self.visit_statement(node.body)

        # Exit loop context
        self.context.exit_loop()

    def visit_for_in_stmt(self, node: ASTNode) -> None:
        """Visit a for-in loop."""
        # Type check iterable
        iterable_type = UNKNOWN
        if node.iterable:
            iterable_type = self.visit_expression(node.iterable)

        # Determine element type
        element_type = UNKNOWN
        if isinstance(iterable_type, ArrayType):
            element_type = iterable_type.element_type
        elif isinstance(iterable_type, SliceType):
            element_type = iterable_type.element_type
        elif iterable_type.equals(STRING):
            element_type = CHAR

        # Update iterator variable type
        if node.iterator:
            iter_symbol = self.symbols.lookup(node.iterator)
            if iter_symbol:
                iter_symbol.type = element_type

        # For indexed for-in, update index variable type
        if node.kind == NodeKind.FOR_IN_INDEXED and node.index_var:
            index_symbol = self.symbols.lookup(node.index_var)
            if index_symbol:
                index_symbol.type = I32  # Index is always i32

        # Enter loop context
        self.context.enter_loop()

        # Visit body
        if node.body:
            self.visit_statement(node.body)

        # Exit loop context
        self.context.exit_loop()

    def visit_match_stmt(self, node: ASTNode) -> None:
        """Visit a match statement."""
        # Type check the match value
        if node.expression:
            self.visit_expression(node.expression)

        # Visit all case branches
        if node.cases:
            for case in node.cases:
                if case.statements:
                    for stmt in case.statements:
                        self.visit_statement(stmt)

        # Visit else case
        if node.else_case:
            for stmt in node.else_case:
                self.visit_statement(stmt)

    def visit_return_stmt(self, node: ASTNode) -> None:
        """Visit a return statement."""
        # Type check return value
        return_type = None
        if node.expression:
            return_type = self.visit_expression(node.expression)

        # Validate against function return type
        if not self.context.validate_return(return_type):
            expected = self.context.get_function_return_type()
            if expected:
                self.add_type_error(
                    TypeErrorType.RETURN_TYPE_MISMATCH,
                    node.span,
                    expected_type=str(expected),
                    got_type=str(return_type)
                )
            else:
                self.add_type_error(TypeErrorType.RETURN_TYPE_MISMATCH, node.span, expected_type="void", context="Cannot return value from void function")

        # Mark function as having return
        self.context.mark_function_returns()

    def visit_expression(self, node: ASTNode) -> Type:
        """
        Visit an expression and return its type.

        Args:
            node: Expression node

        Returns:
            Type of the expression
        """
        expr_type = self._visit_expression_impl(node)
        self.set_type(node, expr_type)
        return expr_type

    def _visit_expression_impl(self, node: ASTNode) -> Type:
        """Internal implementation of expression type checking."""
        if node.kind == NodeKind.LITERAL:
            return self.visit_literal(node)
        elif node.kind == NodeKind.IDENTIFIER:
            return self.visit_identifier(node)
        elif node.kind == NodeKind.BINARY:
            return self.visit_binary_expr(node)
        elif node.kind == NodeKind.UNARY:
            return self.visit_unary_expr(node)
        elif node.kind == NodeKind.CALL:
            return self.visit_call_expr(node)
        elif node.kind == NodeKind.INDEX:
            return self.visit_index_expr(node)
        elif node.kind == NodeKind.FIELD_ACCESS:
            return self.visit_field_access(node)
        elif node.kind == NodeKind.ADDRESS_OF:
            return self.visit_address_of(node)
        elif node.kind == NodeKind.DEREF:
            return self.visit_deref(node)
        elif node.kind == NodeKind.CAST:
            return self.visit_cast(node)
        elif node.kind == NodeKind.IF_EXPR:
            return self.visit_if_expr(node)
        elif node.kind == NodeKind.STRUCT_INIT:
            return self.visit_struct_init(node)
        elif node.kind == NodeKind.ARRAY_INIT:
            return self.visit_array_init(node)
        elif node.kind == NodeKind.NEW_EXPR:
            return self.visit_new_expr(node)
        else:
            error = SemanticError.from_type(SemanticErrorType.UNEXPECTED_NODE_KIND, span=node.span, filename=self.current_file, source_lines=self.source_lines, context=f"Unknown expression kind: {node.kind}")
            self.errors.append(error)
            return UNKNOWN

    def visit_literal(self, node: ASTNode) -> Type:
        """Visit a literal expression."""
        if node.literal_kind == LiteralKind.INTEGER:
            return I32  # Default integer type
        elif node.literal_kind == LiteralKind.FLOAT:
            return F64  # Default float type
        elif node.literal_kind == LiteralKind.CHAR:
            return CHAR
        elif node.literal_kind == LiteralKind.STRING:
            return STRING
        elif node.literal_kind == LiteralKind.BOOLEAN:
            return BOOL
        elif node.literal_kind == LiteralKind.NIL:
            return UNKNOWN  # nil type depends on context
        return UNKNOWN

    def visit_identifier(self, node: ASTNode) -> Type:
        """Visit an identifier expression."""
        ident_name = node.name or ""
        symbol = self.symbols.lookup(ident_name)

        if symbol:
            # Mark as used
            self.symbols.mark_used(ident_name)
            return symbol.type
        else:
            self.add_type_error(TypeErrorType.UNDEFINED_TYPE, node.span, context=f"Identifier '{ident_name}'")
            return UNKNOWN

    def visit_binary_expr(self, node: ASTNode) -> Type:
        """Visit a binary expression."""
        left_type = self.visit_expression(node.left) if node.left else UNKNOWN
        right_type = self.visit_expression(node.right) if node.right else UNKNOWN

        op = node.operator

        # Arithmetic operators: +, -, *, /, %
        if op in {BinaryOp.ADD, BinaryOp.SUB, BinaryOp.MUL, BinaryOp.DIV, BinaryOp.MOD}:
            if not left_type.is_numeric() or not right_type.is_numeric():
                self.add_type_error(TypeErrorType.REQUIRES_NUMERIC_TYPE, node.span)
                return UNKNOWN
            # Result type is the wider of the two
            return left_type if left_type.is_floating() else right_type

        # Comparison operators: ==, !=, <, <=, >, >=
        elif op in {BinaryOp.EQ, BinaryOp.NE, BinaryOp.LT, BinaryOp.LE, BinaryOp.GT, BinaryOp.GE}:
            return BOOL

        # Logical operators: and, or
        elif op in {BinaryOp.AND, BinaryOp.OR}:
            if not left_type.equals(BOOL) or not right_type.equals(BOOL):
                self.add_type_error(TypeErrorType.REQUIRES_BOOL_TYPE, node.span)
            return BOOL

        # Bitwise operators: &, |, ^, <<, >>
        elif op in {BinaryOp.BIT_AND, BinaryOp.BIT_OR, BinaryOp.BIT_XOR, BinaryOp.BIT_SHL, BinaryOp.BIT_SHR}:
            if not left_type.is_integral() or not right_type.is_integral():
                self.add_type_error(TypeErrorType.REQUIRES_INTEGER_TYPE, node.span)
                return UNKNOWN
            return left_type

        return UNKNOWN

    def visit_unary_expr(self, node: ASTNode) -> Type:
        """Visit a unary expression."""
        operand_type = self.visit_expression(node.operand) if node.operand else UNKNOWN

        op = node.operator

        if op == UnaryOp.NEG:
            if not operand_type.is_numeric():
                self.add_type_error(TypeErrorType.REQUIRES_NUMERIC_TYPE, node.span)
            return operand_type

        elif op == UnaryOp.NOT:
            if not operand_type.equals(BOOL):
                self.add_type_error(TypeErrorType.REQUIRES_BOOL_TYPE, node.span)
            return BOOL

        elif op == UnaryOp.BIT_NOT:
            if not operand_type.is_integral():
                self.add_type_error(TypeErrorType.REQUIRES_INTEGER_TYPE, node.span)
            return operand_type

        return UNKNOWN

    def visit_call_expr(self, node: ASTNode) -> Type:
        """Visit a function call expression."""
        # Get function type
        func_type = self.visit_expression(node.function) if node.function else UNKNOWN

        if not isinstance(func_type, FunctionType):
            # Use the span of the function being called, not the whole call expression
            error_span = node.function.span if node.function else node.span

            # Provide better context for unknown types
            if isinstance(func_type, UnknownType):
                # Try to get a meaningful name for what's being called
                if hasattr(node.function, 'kind'):
                    if node.function.kind == NodeKind.FIELD_ACCESS:
                        obj_name = node.function.object.name if hasattr(node.function.object, 'name') else "expression"
                        method_name = node.function.field or "method"
                        context = f"Cannot call '{obj_name}.{method_name}' (undefined identifier)"
                    elif node.function.kind == NodeKind.IDENTIFIER:
                        func_name = node.function.name or "expression"
                        context = f"Cannot call undefined identifier '{func_name}'"
                    else:
                        context = "Cannot call undefined expression"
                    self.add_type_error(TypeErrorType.NOT_CALLABLE, error_span, context=context)
                else:
                    self.add_type_error(TypeErrorType.NOT_CALLABLE, error_span, got_type=str(func_type))
            else:
                self.add_type_error(TypeErrorType.NOT_CALLABLE, error_span, got_type=str(func_type))
            return UNKNOWN

        # Type check arguments
        arg_types = []
        if node.arguments:
            for arg in node.arguments:
                arg_types.append(self.visit_expression(arg))

        # Check argument count
        expected_count = len(func_type.param_types)
        actual_count = len(arg_types)

        if not func_type.is_variadic and actual_count != expected_count:
            self.add_type_error(
                TypeErrorType.WRONG_ARGUMENT_COUNT,
                node.span,
                context=f"Expected {expected_count} arguments, got {actual_count}"
            )

        # Check argument types
        for i, (arg_type, param_type) in enumerate(zip(arg_types, func_type.param_types)):
            if not arg_type.is_assignable_to(param_type):
                self.add_type_error(
                    TypeErrorType.ARGUMENT_TYPE_MISMATCH,
                    node.span,
                    expected_type=str(param_type),
                    got_type=str(arg_type),
                    context=f"Argument {i+1}"
                )

        return func_type.return_type if func_type.return_type else VOID

    def visit_index_expr(self, node: ASTNode) -> Type:
        """Visit an index expression."""
        obj_type = self.visit_expression(node.object) if node.object else UNKNOWN

        if isinstance(obj_type, ArrayType):
            return obj_type.element_type
        elif isinstance(obj_type, SliceType):
            return obj_type.element_type
        elif obj_type.equals(STRING):
            return CHAR
        else:
            self.add_type_error(TypeErrorType.CANNOT_INDEX_TYPE, node.span, got_type=str(obj_type))
            return UNKNOWN

    def visit_field_access(self, node: ASTNode) -> Type:
        """Visit a field access expression."""
        obj_type = self.visit_expression(node.object) if node.object else UNKNOWN
        field_name = node.field or ""

        if isinstance(obj_type, StructType):
            field = obj_type.get_field(field_name)
            if field:
                return field.field_type
            else:
                self.add_type_error(TypeErrorType.NO_SUCH_FIELD, node.span, context=f"Struct '{obj_type}' has no field '{field_name}'")
                return UNKNOWN
        elif isinstance(obj_type, EnumType):
            # Enum variant access: EnumName.VariantName
            if obj_type.has_variant(field_name):
                return obj_type  # Enum variant has the enum type
            else:
                self.add_type_error(TypeErrorType.NO_SUCH_FIELD, node.span, context=f"Enum '{obj_type}' has no variant '{field_name}'")
                return UNKNOWN
        else:
            # Use the span of the object being accessed, not the whole field access
            error_span = node.object.span if node.object else node.span

            # Provide better context for unknown types
            if isinstance(obj_type, UnknownType):
                # Get the object name if available
                obj_name = node.object.name if hasattr(node.object, 'name') and node.object.name else "expression"
                accessed_field = node.field or "field"
                context = f"Cannot access field '{accessed_field}' on undefined identifier '{obj_name}'"
                self.add_type_error(TypeErrorType.FIELD_ACCESS_ON_NON_STRUCT, error_span, context=context)
            else:
                self.add_type_error(TypeErrorType.FIELD_ACCESS_ON_NON_STRUCT, error_span, got_type=str(obj_type))
            return UNKNOWN

    def visit_address_of(self, node: ASTNode) -> Type:
        """Visit an address-of expression (.adr)."""
        operand_type = self.visit_expression(node.operand) if node.operand else UNKNOWN
        return PointerType(pointee_type=operand_type)

    def visit_deref(self, node: ASTNode) -> Type:
        """Visit a dereference expression (.val)."""
        ptr_type = self.visit_expression(node.pointer) if node.pointer else UNKNOWN

        if isinstance(ptr_type, PointerType):
            return ptr_type.pointee_type
        elif isinstance(ptr_type, ReferenceType):
            return ptr_type.referent_type
        else:
            self.add_type_error(TypeErrorType.REQUIRES_POINTER_TYPE, node.span, got_type=str(ptr_type))
            return UNKNOWN

    def visit_cast(self, node: ASTNode) -> Type:
        """Visit a cast expression."""
        # Just return target type (actual cast validation would be more complex)
        return self.resolve_type_node(node.target_type)

    def visit_if_expr(self, node: ASTNode) -> Type:
        """Visit an if expression."""
        # Condition must be bool
        if node.condition:
            cond_type = self.visit_expression(node.condition)
            if not cond_type.equals(BOOL):
                self.add_type_error(TypeErrorType.CONDITION_NOT_BOOL, node.condition.span, expected_type="bool")

        # Both branches must have compatible types
        then_type = self.visit_expression(node.then_expr) if node.then_expr else VOID
        else_type = self.visit_expression(node.else_expr) if node.else_expr else VOID

        if not then_type.equals(else_type):
            self.add_type_error(
                TypeErrorType.IF_EXPR_TYPE_MISMATCH,
                node.span,
                expected_type=str(then_type),
                got_type=str(else_type)
            )

        return then_type

    def visit_struct_init(self, node: ASTNode) -> Type:
        """Visit a struct initialization."""
        # Resolve struct type
        # struct_type might be a string (type name) or an ASTNode
        if node.struct_type:
            if isinstance(node.struct_type, str):
                # Look up type by name
                symbol = self.symbols.lookup(node.struct_type)
                return symbol.type if symbol else UNKNOWN
            else:
                return self.resolve_type_node(node.struct_type)
        return UNKNOWN

    def visit_array_init(self, node: ASTNode) -> Type:
        """Visit an array initialization."""
        # Infer element type from first element
        if node.elements and len(node.elements) > 0:
            elem_type = self.visit_expression(node.elements[0])
            size = len(node.elements)
            return ArrayType(element_type=elem_type, size=size)

        return UNKNOWN

    def visit_new_expr(self, node: ASTNode) -> Type:
        """Visit a new expression."""
        # new T returns ref T
        alloc_type = self.resolve_type_node(node.target_type) if node.target_type else UNKNOWN
        return ReferenceType(referent_type=alloc_type)
