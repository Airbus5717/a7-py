"""
Name resolution pass for A7 semantic analysis.

Builds symbol tables, resolves names to declarations, and validates
scoping rules.
"""

from typing import Optional, List

from src.ast_nodes import ASTNode, NodeKind
from src.symbol_table import SymbolTable, Symbol, SymbolKind, ModuleTable
from src.types import Type, UNKNOWN, get_primitive_type, GenericParamType
from src.errors import SemanticError, SemanticErrorType, SourceSpan


class NameResolutionPass:
    """
    First pass of semantic analysis.

    Walks the AST to:
    1. Build symbol tables for all scopes
    2. Register all declarations
    3. Detect name collisions
    4. Prepare for type checking

    Does NOT perform type checking - that's in the next pass.
    """

    def __init__(self):
        """Initialize name resolution pass."""
        self.symbols = SymbolTable()
        self.modules = ModuleTable()
        self.errors: List[SemanticError] = []
        self.current_file: str = "<unknown>"
        self.source_lines: List[str] = []

    def analyze(self, program: ASTNode, filename: str = "<unknown>") -> SymbolTable:
        """
        Perform name resolution on a program.

        Args:
            program: Root program node
            filename: Source file name (for error messages)

        Returns:
            Symbol table with all declarations

        Note:
            Collects ALL errors instead of stopping at the first one.
            Check self.errors after calling to see if there were any issues.
        """
        self.current_file = filename
        self.errors = []

        # Visit the program
        self.visit_program(program)

        # Return symbol table - caller should check self.errors
        return self.symbols

    def add_error(
        self,
        error_type: SemanticErrorType,
        span: Optional[SourceSpan] = None,
        context: Optional[str] = None,
    ) -> None:
        """Add a semantic error with structured type."""
        error = SemanticError.from_type(
            error_type,
            span=span,
            filename=self.current_file,
            source_lines=self.source_lines,
            context=context,
        )
        self.errors.append(error)

    # Visitor methods

    def visit_program(self, node: ASTNode) -> None:
        """Visit program root."""
        if node.kind != NodeKind.PROGRAM:
            self.add_error(
                SemanticErrorType.UNEXPECTED_NODE_KIND,
                node.span,
                f"Expected program node, got {node.kind}"
            )
            return

        # Process all declarations
        for decl in node.declarations or []:
            self.visit_declaration(decl)

    def visit_declaration(self, node: ASTNode) -> None:
        """Visit a top-level declaration."""
        if node.kind == NodeKind.IMPORT:
            self.visit_import(node)
        elif node.kind == NodeKind.FUNCTION:
            self.visit_function_decl(node)
        elif node.kind == NodeKind.STRUCT:
            self.visit_struct_decl(node)
        elif node.kind == NodeKind.ENUM:
            self.visit_enum_decl(node)
        elif node.kind == NodeKind.UNION:
            self.visit_union_decl(node)
        elif node.kind == NodeKind.TYPE_ALIAS:
            self.visit_type_alias(node)
        elif node.kind == NodeKind.CONST:
            self.visit_const_decl(node)
        elif node.kind == NodeKind.VAR:
            self.visit_var_decl(node)
        else:
            self.add_error(SemanticErrorType.UNEXPECTED_NODE_KIND, node.span, f"declaration kind: {node.kind}")

    def visit_import(self, node: ASTNode) -> None:
        """Visit an import declaration."""
        # Import resolution will be handled by ModuleResolver
        # For now, just register the import intent
        module_path = node.module_path or "<unknown>"

        if node.alias:
            # import "io" as console
            self.modules.add_alias(node.alias, module_path)
        elif node.is_using:
            # using import "io"
            self.modules.add_using_import(module_path)
        elif node.imported_items:
            # import "vector" { Vec3, dot }
            for item in node.imported_items:
                self.modules.add_named_import(item, module_path)

    def visit_function_decl(self, node: ASTNode) -> None:
        """Visit a function declaration."""
        func_name = node.name or "<anonymous>"

        # Register generic parameters first
        if node.generic_params:
            self.symbols.enter_scope(f"generic_{func_name}")
            for gparam in node.generic_params:
                self.visit_generic_param(gparam)

        # Create function symbol (type will be determined in type checking pass)
        func_symbol = Symbol(
            name=func_name,
            kind=SymbolKind.FUNCTION,
            type=UNKNOWN,  # Will be resolved by type checker
            node=node,
            is_mutable=False
        )

        # Register in current scope
        if not self.symbols.define(func_symbol):
            self.add_error(SemanticErrorType.ALREADY_DEFINED, node.span, f"Function '{func_name}'")
            return

        # Enter function scope
        self.symbols.enter_scope(f"function_{func_name}")

        # Register parameters
        if node.parameters:
            for param in node.parameters:
                self.visit_parameter(param)

        # Visit function body
        if node.body:
            self.visit_statement(node.body)

        # Exit function scope
        self.symbols.exit_scope()

        # Exit generic scope if present
        if node.generic_params:
            self.symbols.exit_scope()

    def visit_generic_param(self, node: ASTNode) -> None:
        """Visit a generic parameter declaration."""
        if node.kind != NodeKind.GENERIC_PARAM:
            self.add_error(SemanticErrorType.UNEXPECTED_NODE_KIND, node.span, f"Expected generic param, got {node.kind}")
            return

        param_name = node.name or "<unknown>"

        # Create generic parameter symbol
        # The constraint will be resolved by type checker
        generic_symbol = Symbol(
            name=param_name,
            kind=SymbolKind.GENERIC_PARAM,
            type=UNKNOWN,  # Will be GenericParamType in type checker
            node=node,
            is_mutable=False
        )

        if not self.symbols.define(generic_symbol):
            self.add_error(SemanticErrorType.DUPLICATE_GENERIC_PARAM, node.span, f"Generic parameter '{param_name}'")

    def visit_parameter(self, node: ASTNode) -> None:
        """Visit a function parameter."""
        if node.kind != NodeKind.PARAMETER:
            self.add_error(SemanticErrorType.UNEXPECTED_NODE_KIND, node.span, f"Expected parameter, got {node.kind}")
            return

        param_name = node.name or "<unknown>"

        # Create parameter symbol (type will be resolved by type checker)
        param_symbol = Symbol(
            name=param_name,
            kind=SymbolKind.VARIABLE,
            type=UNKNOWN,
            node=node,
            is_mutable=False  # Parameters are immutable by default
        )

        if not self.symbols.define(param_symbol):
            self.add_error(SemanticErrorType.ALREADY_DEFINED, node.span, f"Parameter '{param_name}'")

    def visit_struct_decl(self, node: ASTNode) -> None:
        """Visit a struct declaration."""
        struct_name = node.name or "<anonymous>"

        # Create struct symbol
        struct_symbol = Symbol(
            name=struct_name,
            kind=SymbolKind.STRUCT,
            type=UNKNOWN,  # Will be StructType in type checker
            node=node,
            is_mutable=False
        )

        if not self.symbols.define(struct_symbol):
            self.add_error(SemanticErrorType.ALREADY_DEFINED, node.span, f"Struct '{struct_name}'")
            return

        # Enter struct scope for fields
        self.symbols.enter_scope(f"struct_{struct_name}")

        # Register fields (just names, types resolved later)
        if node.fields:
            for field in node.fields:
                if field.kind == NodeKind.FIELD:
                    field_name = field.name or "<unknown>"
                    field_symbol = Symbol(
                        name=field_name,
                        kind=SymbolKind.VARIABLE,
                        type=UNKNOWN,
                        node=field,
                        is_mutable=False
                    )
                    if not self.symbols.define(field_symbol):
                        self.add_error(SemanticErrorType.DUPLICATE_FIELD, field.span, f"'{field_name}' in struct '{struct_name}'")

        self.symbols.exit_scope()

    def visit_enum_decl(self, node: ASTNode) -> None:
        """Visit an enum declaration."""
        enum_name = node.name or "<anonymous>"

        # Create enum symbol
        enum_symbol = Symbol(
            name=enum_name,
            kind=SymbolKind.ENUM,
            type=UNKNOWN,  # Will be EnumType in type checker
            node=node,
            is_mutable=False
        )

        if not self.symbols.define(enum_symbol):
            self.add_error(SemanticErrorType.ALREADY_DEFINED, node.span, f"Enum '{enum_name}'")
            return

        # Register variants
        if node.variants:
            for variant in node.variants:
                if variant.kind == NodeKind.ENUM_VARIANT:
                    variant_name = variant.name or "<unknown>"
                    # Enum variants are accessible as EnumName.VariantName
                    # They're also sometimes directly accessible depending on language semantics
                    variant_symbol = Symbol(
                        name=f"{enum_name}.{variant_name}",
                        kind=SymbolKind.ENUM_VARIANT,
                        type=UNKNOWN,
                        node=variant,
                        is_mutable=False
                    )
                    self.symbols.define(variant_symbol)

    def visit_union_decl(self, node: ASTNode) -> None:
        """Visit a union declaration."""
        union_name = node.name or "<anonymous>"

        # Create union symbol
        union_symbol = Symbol(
            name=union_name,
            kind=SymbolKind.UNION,
            type=UNKNOWN,  # Will be UnionType in type checker
            node=node,
            is_mutable=False
        )

        if not self.symbols.define(union_symbol):
            self.add_error(SemanticErrorType.ALREADY_DEFINED, node.span, f"Union '{union_name}'")
            return

        # Enter union scope for fields
        self.symbols.enter_scope(f"union_{union_name}")

        # Register fields
        if node.fields:
            for field in node.fields:
                if field.kind == NodeKind.FIELD:
                    field_name = field.name or "<unknown>"
                    field_symbol = Symbol(
                        name=field_name,
                        kind=SymbolKind.VARIABLE,
                        type=UNKNOWN,
                        node=field,
                        is_mutable=False
                    )
                    if not self.symbols.define(field_symbol):
                        self.add_error(SemanticErrorType.DUPLICATE_FIELD, field.span, f"'{field_name}' in union '{union_name}'")

        self.symbols.exit_scope()

    def visit_type_alias(self, node: ASTNode) -> None:
        """Visit a type alias declaration."""
        alias_name = node.name or "<anonymous>"

        # Create type alias symbol
        alias_symbol = Symbol(
            name=alias_name,
            kind=SymbolKind.TYPE,
            type=UNKNOWN,  # Will be resolved in type checker
            node=node,
            is_mutable=False
        )

        if not self.symbols.define(alias_symbol):
            self.add_error(SemanticErrorType.ALREADY_DEFINED, node.span, f"Type alias '{alias_name}'")

    def visit_const_decl(self, node: ASTNode) -> None:
        """Visit a constant declaration."""
        const_name = node.name or "<unknown>"

        # Create constant symbol
        const_symbol = Symbol(
            name=const_name,
            kind=SymbolKind.CONSTANT,
            type=UNKNOWN,  # Will be inferred in type checker
            node=node,
            is_mutable=False
        )

        if not self.symbols.define(const_symbol):
            self.add_error(SemanticErrorType.ALREADY_DEFINED, node.span, f"Constant '{const_name}'")

    def visit_var_decl(self, node: ASTNode) -> None:
        """Visit a variable declaration."""
        var_name = node.name or "<unknown>"

        # Create variable symbol
        var_symbol = Symbol(
            name=var_name,
            kind=SymbolKind.VARIABLE,
            type=UNKNOWN,  # Will be inferred or explicitly typed in type checker
            node=node,
            is_mutable=True
        )

        if not self.symbols.define(var_symbol):
            self.add_error(SemanticErrorType.ALREADY_DEFINED, node.span, f"Variable '{var_name}'")

    def visit_statement(self, node: ASTNode) -> None:
        """Visit a statement."""
        if node.kind == NodeKind.BLOCK:
            self.visit_block(node)
        elif node.kind == NodeKind.VAR:
            self.visit_var_decl(node)
        elif node.kind == NodeKind.CONST:
            self.visit_const_decl(node)
        elif node.kind == NodeKind.IF_STMT:
            self.visit_if_stmt(node)
        elif node.kind == NodeKind.WHILE:
            self.visit_while_stmt(node)
        elif node.kind == NodeKind.FOR:
            self.visit_for_stmt(node)
        elif node.kind == NodeKind.FOR_IN:
            self.visit_for_in_stmt(node)
        elif node.kind == NodeKind.FOR_IN_INDEXED:
            self.visit_for_in_indexed_stmt(node)
        elif node.kind == NodeKind.MATCH:
            self.visit_match_stmt(node)
        elif node.kind == NodeKind.RETURN:
            # Return statements don't introduce names
            pass
        elif node.kind == NodeKind.BREAK:
            # Break statements don't introduce names
            pass
        elif node.kind == NodeKind.CONTINUE:
            # Continue statements don't introduce names
            pass
        elif node.kind == NodeKind.DEFER:
            # Defer statements don't introduce names (expression handled separately)
            pass
        elif node.kind == NodeKind.DEL:
            # Del statements don't introduce names
            pass
        elif node.kind == NodeKind.ASSIGNMENT:
            # Assignments don't introduce names (lhs must already exist)
            pass
        elif node.kind == NodeKind.EXPRESSION_STMT:
            # Expression statements don't introduce names
            pass

    def visit_block(self, node: ASTNode) -> None:
        """Visit a block statement."""
        # Enter new scope for block
        self.symbols.enter_scope("block")

        # Visit all statements in block
        if node.statements:
            for stmt in node.statements:
                self.visit_statement(stmt)

        # Exit block scope
        self.symbols.exit_scope()

    def visit_if_stmt(self, node: ASTNode) -> None:
        """Visit an if statement."""
        # Then branch
        if node.then_stmt:
            if node.then_stmt.kind == NodeKind.BLOCK:
                self.visit_statement(node.then_stmt)
            else:
                # Single statement - create implicit scope
                self.symbols.enter_scope("if_then")
                self.visit_statement(node.then_stmt)
                self.symbols.exit_scope()

        # Else branch
        if node.else_stmt:
            if node.else_stmt.kind == NodeKind.BLOCK:
                self.visit_statement(node.else_stmt)
            else:
                # Single statement - create implicit scope
                self.symbols.enter_scope("if_else")
                self.visit_statement(node.else_stmt)
                self.symbols.exit_scope()

    def visit_while_stmt(self, node: ASTNode) -> None:
        """Visit a while loop."""
        if node.body:
            if node.body.kind == NodeKind.BLOCK:
                self.visit_statement(node.body)
            else:
                self.symbols.enter_scope("while")
                self.visit_statement(node.body)
                self.symbols.exit_scope()

    def visit_for_stmt(self, node: ASTNode) -> None:
        """Visit a C-style for loop."""
        # For loop has its own scope
        self.symbols.enter_scope("for")

        # Init statement may declare variables
        if node.init:
            self.visit_statement(node.init)

        # Visit body
        if node.body:
            self.visit_statement(node.body)

        self.symbols.exit_scope()

    def visit_for_in_stmt(self, node: ASTNode) -> None:
        """Visit a for-in loop."""
        # For-in loop has its own scope
        self.symbols.enter_scope("for_in")

        # Register iterator variable
        iterator_name = node.iterator or "<unknown>"
        iter_symbol = Symbol(
            name=iterator_name,
            kind=SymbolKind.VARIABLE,
            type=UNKNOWN,  # Will be inferred from iterable type
            node=node,
            is_mutable=False  # Iterator is immutable
        )

        if not self.symbols.define(iter_symbol):
            self.add_error(SemanticErrorType.ALREADY_DEFINED, node.span, f"Iterator variable '{iterator_name}'")

        # Visit body
        if node.body:
            self.visit_statement(node.body)

        self.symbols.exit_scope()

    def visit_for_in_indexed_stmt(self, node: ASTNode) -> None:
        """Visit an indexed for-in loop."""
        # For-in loop has its own scope
        self.symbols.enter_scope("for_in_indexed")

        # Register index variable
        index_name = node.index_var or "<unknown>"
        index_symbol = Symbol(
            name=index_name,
            kind=SymbolKind.VARIABLE,
            type=UNKNOWN,  # Will be integer type
            node=node,
            is_mutable=False
        )

        if not self.symbols.define(index_symbol):
            self.add_error(SemanticErrorType.ALREADY_DEFINED, node.span, f"Index variable '{index_name}'")

        # Register iterator variable
        iterator_name = node.iterator or "<unknown>"
        iter_symbol = Symbol(
            name=iterator_name,
            kind=SymbolKind.VARIABLE,
            type=UNKNOWN,
            node=node,
            is_mutable=False
        )

        if not self.symbols.define(iter_symbol):
            self.add_error(SemanticErrorType.ALREADY_DEFINED, node.span, f"Iterator variable '{iterator_name}'")

        # Visit body
        if node.body:
            self.visit_statement(node.body)

        self.symbols.exit_scope()

    def visit_match_stmt(self, node: ASTNode) -> None:
        """Visit a match statement."""
        # Each case branch gets its own scope
        if node.cases:
            for case in node.cases:
                if case.kind == NodeKind.CASE_BRANCH:
                    self.symbols.enter_scope("match_case")

                    # Visit case body
                    if case.statements:
                        for stmt in case.statements:
                            self.visit_statement(stmt)

                    self.symbols.exit_scope()

        # Else case
        if node.else_case:
            self.symbols.enter_scope("match_else")
            for stmt in node.else_case:
                self.visit_statement(stmt)
            self.symbols.exit_scope()

    def get_module_table(self) -> ModuleTable:
        """Get the module table."""
        return self.modules
