"""
Rich console output formatter for A7 compiler.

Provides beautiful, detailed output for tokenization, parsing, and AST display.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree
from rich.syntax import Syntax


class ConsoleFormatter:
    """Formats compilation results for Rich console display."""

    def __init__(self, tokenize_only: bool = False, parse_only: bool = False):
        """
        Initialize console formatter.

        Args:
            tokenize_only: Only show tokenization output
            parse_only: Show tokenization and parsing output
        """
        self.tokenize_only = tokenize_only
        self.parse_only = parse_only
        self.console = Console()

    def display_compilation(self, tokens: list, ast, source_code: str, input_path: str):
        """
        Display compilation results in Rich format.

        Args:
            tokens: List of tokens from tokenizer
            ast: AST root node
            source_code: Original source code
            input_path: Input file path
        """
        # Show source code panel
        self._display_source_panel(source_code, input_path)

        # Show tokenization results
        self._display_tokens(tokens)

        # Show parsing results (unless tokenize-only)
        if not self.tokenize_only:
            self._display_ast(ast)

        # Summary
        self.console.print(f"\n[bold dim]Analysis complete[/bold dim]")

    def _display_source_panel(self, source_code: str, input_path: str):
        """Display source code with syntax highlighting."""
        if self.tokenize_only:
            title = f"Tokenization: {input_path}"
        elif self.parse_only:
            title = f"Parsing: {input_path}"
        else:
            title = f"Compilation: {input_path}"

        # Use syntax highlighting for A7 code (fallback to text)
        try:
            source_syntax = Syntax(
                source_code, "rust", theme="monokai", line_numbers=True
            )
        except:
            source_syntax = source_code

        code_panel = Panel(source_syntax, title=title, border_style="blue")
        self.console.print(code_panel)

    def _display_tokens(self, tokens: list):
        """Display tokenization results in a table."""
        self.console.print("\n[bold cyan]TOKENIZATION RESULTS[/bold cyan]")

        token_table = Table(show_header=True, header_style="bold magenta")
        token_table.add_column("Pos", style="dim", width=6)
        token_table.add_column("Line:Col", style="cyan", width=8)
        token_table.add_column("Token Type", style="green", width=16)
        token_table.add_column("Value", style="yellow")
        token_table.add_column("Length", style="dim", width=6)

        for i, token in enumerate(tokens):
            if token.type.name == "EOF":
                continue  # Skip EOF for cleaner display

            token_table.add_row(
                str(i),
                f"{token.line}:{token.column}",
                token.type.name,
                repr(token.value) if token.value else "''",
                str(token.length) if hasattr(token, "length") else "?",
            )

        self.console.print(token_table)
        self.console.print(
            f"[dim]Total tokens: {len([t for t in tokens if t.type.name != 'EOF'])}[/dim]"
        )

    def _display_ast(self, ast):
        """Display AST structure as a tree."""
        self.console.print("\n[bold cyan]PARSING RESULTS[/bold cyan]")

        if ast:
            self.console.print("[green]Successfully parsed into AST[/green]")

            # AST summary
            summary_text = Text()
            summary_text.append("AST Root: ", style="bold")
            summary_text.append(f"{ast.kind.name}", style="cyan bold")
            if hasattr(ast, "declarations") and ast.declarations:
                summary_text.append(
                    f" with {len(ast.declarations)} top-level declarations",
                    style="dim",
                )
            self.console.print(summary_text)

            # AST tree structure
            if hasattr(ast, "declarations") and ast.declarations:
                tree = Tree("Program")
                for decl in ast.declarations:
                    decl_node = tree.add(self.format_declaration_node(decl))

                    # Add function body details
                    if (
                        hasattr(decl, "body")
                        and decl.body
                        and hasattr(decl.body, "statements")
                        and decl.body.statements is not None
                    ):
                        self._add_statements_to_tree(
                            decl_node, decl.body.statements
                        )

                self.console.print(tree)

            # Stop here for parse-only mode
            if self.parse_only:
                self.console.print(
                    "\n[bold dim]Stopping before code generation[/bold dim]"
                )
        else:
            self.console.print("[red]Failed to parse AST[/red]")
            self.console.print(
                "[dim]Check tokenization output above for potential issues[/dim]"
            )

    def format_declaration_node(self, decl) -> str:
        """Format a declaration node for tree display."""
        label = f"[green]{decl.kind.name}[/green]"

        if hasattr(decl, "name") and decl.name:
            label += f" [yellow]{decl.name}[/yellow]"

        # Add parameters with types for functions
        if decl.kind.name == "FUNCTION":
            if hasattr(decl, "parameters") and decl.parameters:
                params = []
                for param in decl.parameters:
                    param_str = ""
                    if hasattr(param, "name") and param.name:
                        param_str = param.name
                    if hasattr(param, "param_type") and param.param_type:
                        type_str = self.format_type(param.param_type)
                        if param_str:
                            param_str += f": {type_str}"
                        else:
                            param_str = type_str
                    elif not param_str:
                        param_str = "?"
                    params.append(param_str)

                label += f" [blue]({', '.join(params)})[/blue]"
            else:
                label += f" [blue]()[/blue]"

            # Add return type
            if hasattr(decl, "return_type") and decl.return_type:
                ret_type_str = self.format_type(decl.return_type)
                label += f" [cyan]→ {ret_type_str}[/cyan]"
            else:
                label += f" [dim]→ void[/dim]"

        # For other declarations, show type if available
        elif hasattr(decl, "explicit_type") and decl.explicit_type:
            type_str = self.format_type(decl.explicit_type)
            label += f" [cyan]: {type_str}[/cyan]"

        if hasattr(decl, "span") and decl.span:
            label += f" [dim](line {decl.span.start_line})[/dim]"

        return label

    def format_type(self, type_node) -> str:
        """Format a type node for display."""
        if not type_node:
            return "?"

        if hasattr(type_node, "kind"):
            kind = type_node.kind.name

            if kind == "TYPE_PRIMITIVE":
                return (
                    type_node.type_name
                    if hasattr(type_node, "type_name")
                    else "primitive"
                )
            elif kind == "TYPE_IDENTIFIER":
                return (
                    type_node.name
                    if hasattr(type_node, "name")
                    else "identifier"
                )
            elif kind == "TYPE_GENERIC":
                # Generic type like List($T) or Map(K, V)
                base_name = type_node.name if hasattr(type_node, "name") else "?"
                if hasattr(type_node, "type_args") and type_node.type_args:
                    args = [self.format_type(arg) for arg in type_node.type_args]
                    return f"{base_name}({', '.join(args)})"
                return base_name
            elif kind == "TYPE_ARRAY":
                elem_type = (
                    self.format_type(type_node.element_type)
                    if hasattr(type_node, "element_type")
                    else "?"
                )
                if hasattr(type_node, "size") and type_node.size:
                    # Try to get literal value for size
                    if hasattr(type_node.size, "literal_value"):
                        size = str(type_node.size.literal_value)
                    else:
                        size = "?"
                else:
                    size = "?"
                return f"[{size}]{elem_type}"
            elif kind == "TYPE_SLICE":
                elem_type = (
                    self.format_type(type_node.element_type)
                    if hasattr(type_node, "element_type")
                    else "?"
                )
                return f"[]{elem_type}"
            elif kind == "TYPE_POINTER":
                target_type = (
                    self.format_type(type_node.target_type)
                    if hasattr(type_node, "target_type")
                    else "?"
                )
                return f"ref {target_type}"
            elif kind == "TYPE_FUNCTION":
                # Function type like fn(i32, i32) i32
                param_types = []
                if hasattr(type_node, "parameter_types") and type_node.parameter_types:
                    param_types = [self.format_type(pt) for pt in type_node.parameter_types]
                params_str = ", ".join(param_types)

                ret_type = ""
                if hasattr(type_node, "return_type") and type_node.return_type:
                    ret_type = " " + self.format_type(type_node.return_type)

                return f"fn({params_str}){ret_type}"
            elif kind == "TYPE_STRUCT":
                # Inline struct type
                field_count = len(type_node.fields) if hasattr(type_node, "fields") and type_node.fields else 0
                return f"struct {{ {field_count} fields }}"

        # Fallback for simple types or unknown structures
        if hasattr(type_node, "type_name"):
            return type_node.type_name
        elif hasattr(type_node, "name"):
            return type_node.name
        return str(type_node)

    def format_expression_detail(self, expr) -> str:
        """Format expression detail for display in AST tree."""
        if not expr or not hasattr(expr, "kind"):
            return None

        kind = expr.kind.name

        # Function calls - show function name
        if kind == "CALL":
            func_name = "?"
            if hasattr(expr, "function") and expr.function:
                func_expr = expr.function
                # Check if it's a field access (method call) first
                if hasattr(func_expr, "kind") and func_expr.kind.name == "FIELD_ACCESS":
                    obj_name = "_"
                    if hasattr(func_expr, "object") and func_expr.object and hasattr(func_expr.object, "name") and func_expr.object.name:
                        obj_name = func_expr.object.name
                    field_name = "?"
                    if hasattr(func_expr, "field") and func_expr.field:
                        field_name = func_expr.field
                    func_name = f"{obj_name}.{field_name}"
                # Check if it's a simple identifier
                elif hasattr(func_expr, "name") and func_expr.name:
                    func_name = func_expr.name

            arg_count = len(expr.arguments) if hasattr(expr, "arguments") and expr.arguments else 0
            return f"[magenta]call[/magenta] [yellow]{func_name}[/yellow]() [dim]({arg_count} args)[/dim]"

        # Binary operations - show operator
        elif kind == "BINARY":
            op = "?"
            if hasattr(expr, "operator") and expr.operator:
                op = expr.operator.name.lower()
            return f"[magenta]binary_op[/magenta] [cyan]{op}[/cyan]"

        # Unary operations - show operator
        elif kind == "UNARY":
            op = "?"
            if hasattr(expr, "operator") and expr.operator:
                op = expr.operator.name.lower()
            return f"[magenta]unary_op[/magenta] [cyan]{op}[/cyan]"

        # Identifier - show name
        elif kind == "IDENTIFIER":
            name = expr.name if hasattr(expr, "name") else "?"
            return f"[magenta]identifier[/magenta] [yellow]{name}[/yellow]"

        # Literal - show kind and value
        elif kind == "LITERAL":
            lit_kind = "?"
            lit_val = ""
            if hasattr(expr, "literal_kind") and expr.literal_kind:
                lit_kind = expr.literal_kind.name.lower()
            if hasattr(expr, "literal_value"):
                val_str = str(expr.literal_value)
                if len(val_str) > 20:
                    val_str = val_str[:20] + "..."
                lit_val = f" [dim]{val_str}[/dim]"
            return f"[magenta]literal[/magenta] [cyan]{lit_kind}[/cyan]{lit_val}"

        # Field access - show field name
        elif kind == "FIELD_ACCESS":
            field = expr.field if hasattr(expr, "field") else "?"
            return f"[magenta]field_access[/magenta] [yellow].{field}[/yellow]"

        # Array index
        elif kind == "INDEX":
            return f"[magenta]index[/magenta]"

        # Cast expression
        elif kind == "CAST":
            type_str = "?"
            if hasattr(expr, "target_type"):
                type_str = self.format_type(expr.target_type)
            return f"[magenta]cast[/magenta] [cyan]→ {type_str}[/cyan]"

        # If expression
        elif kind == "IF_EXPR":
            return f"[magenta]if_expr[/magenta]"

        # Struct initialization
        elif kind == "STRUCT_INIT":
            type_name = "?"
            if hasattr(expr, "struct_type"):
                type_name = self.format_type(expr.struct_type)
            field_count = len(expr.field_inits) if hasattr(expr, "field_inits") and expr.field_inits else 0
            return f"[magenta]struct_init[/magenta] [cyan]{type_name}[/cyan] [dim]({field_count} fields)[/dim]"

        # Array initialization
        elif kind == "ARRAY_INIT":
            elem_count = len(expr.elements) if hasattr(expr, "elements") and expr.elements else 0
            return f"[magenta]array_init[/magenta] [dim]({elem_count} elements)[/dim]"

        # New expression
        elif kind == "NEW_EXPR":
            type_str = "?"
            if hasattr(expr, "target_type"):
                type_str = self.format_type(expr.target_type)
            return f"[magenta]new[/magenta] [cyan]{type_str}[/cyan]"

        # Default - just show the kind
        else:
            return f"[magenta]{kind.lower()}[/magenta]"

    def format_statement_label(self, stmt) -> str:
        """Format a statement label with detailed information."""
        if not stmt or not hasattr(stmt, "kind"):
            return "[dim]unknown[/dim]"

        kind = stmt.kind.name
        stmt_label = f"[blue]{kind}[/blue]"

        # Variable/Constant declarations
        if kind in ("VAR", "CONST"):
            if hasattr(stmt, "name") and stmt.name:
                stmt_label += f" [yellow]{stmt.name}[/yellow]"
            if hasattr(stmt, "explicit_type") and stmt.explicit_type:
                type_str = self.format_type(stmt.explicit_type)
                stmt_label += f" [cyan]{type_str}[/cyan]"
            if hasattr(stmt, "value") and stmt.value:
                val_detail = self.format_expression_detail(stmt.value)
                if val_detail:
                    stmt_label += f" = {val_detail}"

        # Expression statements - show what kind of expression
        elif kind == "EXPRESSION_STMT":
            if hasattr(stmt, "expression") and stmt.expression:
                expr_detail = self.format_expression_detail(stmt.expression)
                if expr_detail:
                    stmt_label += f" → {expr_detail}"

        # Assignment statements
        elif kind == "ASSIGNMENT":
            if hasattr(stmt, "target"):
                target_name = "?"
                if hasattr(stmt.target, "name"):
                    target_name = stmt.target.name
                elif hasattr(stmt.target, "field"):
                    target_name = f"_.{stmt.target.field}"
                stmt_label += f" [yellow]{target_name}[/yellow]"

            if hasattr(stmt, "operator") and stmt.operator:
                op_str = "="
                if hasattr(stmt.operator, "name"):
                    op_name = stmt.operator.name
                    if op_name == "ASSIGN":
                        op_str = "="
                    elif op_name == "ADD_ASSIGN":
                        op_str = "+="
                    elif op_name == "SUB_ASSIGN":
                        op_str = "-="
                    elif op_name == "MUL_ASSIGN":
                        op_str = "*="
                    elif op_name == "DIV_ASSIGN":
                        op_str = "/="
                    elif op_name == "MOD_ASSIGN":
                        op_str = "%="
                    else:
                        op_str = op_name.replace("_ASSIGN", "").lower() + "="
                stmt_label += f" [cyan]{op_str}[/cyan]"

            if hasattr(stmt, "value") and stmt.value:
                val_detail = self.format_expression_detail(stmt.value)
                if val_detail:
                    stmt_label += f" {val_detail}"

        # Return statements
        elif kind == "RETURN":
            if hasattr(stmt, "value") and stmt.value:
                val_detail = self.format_expression_detail(stmt.value)
                if val_detail:
                    stmt_label += f" {val_detail}"
            else:
                stmt_label += " [dim](void)[/dim]"

        # If statements
        elif kind == "IF_STMT":
            if hasattr(stmt, "condition") and stmt.condition:
                cond_detail = self.format_expression_detail(stmt.condition)
                if cond_detail:
                    stmt_label += f" {cond_detail}"

        # While loops
        elif kind == "WHILE":
            if hasattr(stmt, "condition") and stmt.condition:
                cond_detail = self.format_expression_detail(stmt.condition)
                if cond_detail:
                    stmt_label += f" {cond_detail}"

        # For loops
        elif kind == "FOR":
            parts = []
            if hasattr(stmt, "init") and stmt.init and hasattr(stmt.init, "name"):
                parts.append(f"[yellow]{stmt.init.name}[/yellow]")
            if hasattr(stmt, "condition") and stmt.condition:
                cond_detail = self.format_expression_detail(stmt.condition)
                if cond_detail:
                    parts.append(cond_detail)
            if parts:
                stmt_label += f" ({'; '.join(parts)})"

        # For-in loops
        elif kind in ("FOR_IN", "FOR_IN_INDEXED"):
            if hasattr(stmt, "iterator") and stmt.iterator:
                stmt_label += f" [yellow]{stmt.iterator}[/yellow]"
            if kind == "FOR_IN_INDEXED" and hasattr(stmt, "index_var") and stmt.index_var:
                stmt_label = stmt_label.replace(f" [yellow]{stmt.iterator}[/yellow]",
                                                  f" [yellow]{stmt.index_var}, {stmt.iterator}[/yellow]")
            if hasattr(stmt, "iterable") and stmt.iterable:
                iter_detail = self.format_expression_detail(stmt.iterable)
                if iter_detail:
                    stmt_label += f" in {iter_detail}"

        # Match statements
        elif kind == "MATCH":
            if hasattr(stmt, "expression") and stmt.expression:
                expr_detail = self.format_expression_detail(stmt.expression)
                if expr_detail:
                    stmt_label += f" {expr_detail}"
            if hasattr(stmt, "cases") and stmt.cases:
                stmt_label += f" [dim]({len(stmt.cases)} cases)[/dim]"

        # Break/Continue with labels
        elif kind in ("BREAK", "CONTINUE"):
            if hasattr(stmt, "label") and stmt.label:
                stmt_label += f" [yellow]{stmt.label}[/yellow]"

        # Defer statements
        elif kind == "DEFER":
            if hasattr(stmt, "statement") and stmt.statement:
                deferred_detail = self.format_statement_label(stmt.statement)
                stmt_label += f" → {deferred_detail}"

        # Del statements
        elif kind == "DEL":
            if hasattr(stmt, "expression") and stmt.expression:
                expr_detail = self.format_expression_detail(stmt.expression)
                if expr_detail:
                    stmt_label += f" {expr_detail}"

        # Block statements - show statement count
        elif kind == "BLOCK":
            if hasattr(stmt, "statements") and stmt.statements:
                stmt_label += f" [dim]({len(stmt.statements)} stmts)[/dim]"

        return stmt_label

    def _add_statements_to_tree(self, parent_node, statements):
        """Add statement nodes to the tree."""
        if statements is None:
            return
        for stmt in statements:
            stmt_label = self.format_statement_label(stmt)
            stmt_node = parent_node.add(stmt_label)

            # Recursively add nested statements for blocks and control flow
            if hasattr(stmt, "statements") and stmt.statements:
                self._add_statements_to_tree(stmt_node, stmt.statements)
            elif hasattr(stmt, "then_stmt") and stmt.then_stmt:
                if hasattr(stmt.then_stmt, "statements"):
                    self._add_statements_to_tree(stmt_node, stmt.then_stmt.statements)
                if hasattr(stmt, "else_stmt") and stmt.else_stmt:
                    if hasattr(stmt.else_stmt, "statements"):
                        self._add_statements_to_tree(
                            stmt_node, stmt.else_stmt.statements
                        )
