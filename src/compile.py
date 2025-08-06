"""
A7 to Zig Compiler

Main compilation pipeline that orchestrates lexing, parsing, and code generation.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime
            
console = Console()
from .tokens import Tokenizer, Token
from .parser import Parser, parse_a7  # Now implemented!
# from .backends import get_backend  # Ignoring backend for now
from .errors import CompilerError, display_error, create_error_handler


class A7Compiler:
    """Main compiler class that handles the A7 compilation pipeline with pluggable backends."""
    
    def __init__(self, backend: str = "zig", verbose: bool = False, json_output: bool = False, 
                 tokenize_only: bool = False, parse_only: bool = False):
        self.backend = backend
        self.verbose = verbose
        self.json_output = json_output
        self.tokenize_only = tokenize_only
        self.parse_only = parse_only
        # Tokenizer will be created per file during compilation
        # self.parser = Parser()  # Not yet implemented
        # self.codegen = get_backend(backend)  # Ignoring backend for now
    
    def _compilation_to_json(self, tokens: list[Token], ast, source_code: str, input_path: str) -> dict:
        """Convert compilation results to JSON format."""
        # Convert tokens to serializable format
        token_list = []
        for token in tokens:
            token_list.append({
                "type": token.type.name,
                "value": token.value,
                "line": token.line,
                "column": token.column,
                "length": token.length
            })
        
        # Convert AST to serializable format (comprehensive)
        def ast_to_dict(node):
            if node is None:
                return None
            
            result = {
                "kind": node.kind.name,
                "span": {
                    "start_line": node.span.start_line,
                    "start_column": node.span.start_column,
                    "end_line": node.span.end_line,
                    "end_column": node.span.end_column,
                    "length": getattr(node.span, 'length', None)
                } if node.span else None
            }
            
            # Add all relevant scalar fields
            scalar_fields = [
                'name', 'is_public', 'is_using', 'is_tagged', 'is_variadic', 
                'has_fallthrough', 'module_path', 'alias', 'type_name', 'field',
                'iterator', 'index_var', 'label', 'enum_type', 'variant', 'raw_text'
            ]
            
            for field in scalar_fields:
                value = getattr(node, field, None)
                if value is not None:
                    result[field] = value
            
            # Add literal information
            if hasattr(node, 'literal_kind') and node.literal_kind:
                result["literal_kind"] = node.literal_kind.name
                result["literal_value"] = node.literal_value
                result["raw_text"] = node.raw_text
            
            # Add operator information
            if hasattr(node, 'operator') and node.operator:
                result["operator"] = node.operator.name if hasattr(node.operator, 'name') else str(node.operator)
            
            # Add list fields (child nodes)
            list_fields = [
                'declarations', 'parameters', 'statements', 'arguments', 'fields',
                'variants', 'generic_params', 'type_arguments', 'parameter_types',
                'type_args', 'types', 'elements', 'field_inits', 'cases',
                'else_case', 'patterns', 'imported_items'
            ]
            
            for field in list_fields:
                field_value = getattr(node, field, None)
                if field_value:
                    result[field] = [ast_to_dict(child) for child in field_value]
            
            # Add single node fields
            node_fields = [
                'value', 'body', 'condition', 'left', 'right', 'operand', 'function',
                'expression', 'return_type', 'explicit_type', 'target_type',
                'element_type', 'size', 'object', 'index', 'start', 'end',
                'pointer', 'then_expr', 'else_expr', 'struct_type', 'then_stmt',
                'else_stmt', 'init', 'update', 'iterable', 'statement', 'target',
                'literal', 'param_type', 'field_type', 'variant_type', 'constraint'
            ]
            
            for field in node_fields:
                field_value = getattr(node, field, None)
                if field_value:
                    result[field] = ast_to_dict(field_value)
            
            return result
        
        # Create comprehensive JSON structure
        result = {
            "metadata": {
                "filename": input_path,
                "compiler": "a7-py",
                "backend": self.backend,
                "timestamp": datetime.now().isoformat(),
                "token_count": len(tokens),
                "source_lines": len(source_code.splitlines()),
                "source_size_bytes": len(source_code.encode('utf-8')),
                "parse_success": ast is not None
            },
            "source_code": source_code,
            "tokens": token_list,
            "ast": ast_to_dict(ast) if ast else None
        }
        
        return result
    
    def _display_debug_output(self, tokens: list[Token], ast, source_code: str, input_path: str):
        """Display debug output in Rich format based on current debug mode."""
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.text import Text
        from rich.tree import Tree
        from rich.syntax import Syntax
        
        console = Console()
        
        # Always show source code panel in analysis modes
        if self.tokenize_only:
            title = f"Tokenization: {input_path}"
        elif self.parse_only:
            title = f"Parsing: {input_path}"
        else:
            title = f"Compilation: {input_path}"
        
        # Use syntax highlighting for A7 code (fallback to text)
        try:
            source_syntax = Syntax(source_code, "rust", theme="monokai", line_numbers=True)
        except:
            source_syntax = source_code
        
        code_panel = Panel(
            source_syntax,
            title=title,
            border_style="blue"
        )
        console.print(code_panel)
        
        # Token analysis
        console.print("\n[bold cyan]TOKENIZATION RESULTS[/bold cyan]")
        
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
                str(token.length) if hasattr(token, 'length') else "?"
            )
        
        console.print(token_table)
        console.print(f"[dim]Total tokens: {len([t for t in tokens if t.type.name != 'EOF'])}[/dim]")
        
        # AST analysis (only if not tokenize-only mode)
        if not self.tokenize_only:
            console.print("\n[bold cyan]PARSING RESULTS[/bold cyan]")
            
            if ast:
                console.print("[green]Successfully parsed into AST[/green]")
                
                # AST summary
                summary_text = Text()
                summary_text.append("AST Root: ", style="bold")
                summary_text.append(f"{ast.kind.name}", style="cyan bold")
                if hasattr(ast, 'declarations') and ast.declarations:
                    summary_text.append(f" with {len(ast.declarations)} top-level declarations", style="dim")
                console.print(summary_text)
                
                # AST tree structure
                if hasattr(ast, 'declarations') and ast.declarations:
                    tree = Tree("Program")
                    for i, decl in enumerate(ast.declarations):
                        decl_node = tree.add(self._format_declaration_node(decl))
                        
                        # Add function body details
                        if hasattr(decl, 'body') and decl.body and hasattr(decl.body, 'statements'):
                            self._add_statements_to_tree(decl_node, decl.body.statements)
                
                    console.print(tree)
                
                # Stop here for parse-only mode
                if self.parse_only:
                    console.print("\n[bold dim]Stopping before code generation[/bold dim]")
            else:
                console.print("[red]Failed to parse AST[/red]")
                console.print("[dim]Check tokenization output above for potential issues[/dim]")
        
        # Summary footer
        console.print(f"\n[bold dim]Analysis complete[/bold dim]")
    
    def _format_declaration_node(self, decl):
        """Format a declaration node for tree display."""
        label = f"[green]{decl.kind.name}[/green]"
        
        if hasattr(decl, 'name'):
            label += f" [yellow]{decl.name}[/yellow]"
            
        # Add parameters inline for functions
        if hasattr(decl, 'parameters') and decl.parameters:
            params = []
            for param in decl.parameters:
                if hasattr(param, 'name'):
                    params.append(param.name)
            
            if params:
                label += f" [blue]({', '.join(params)})[/blue]"
        
        if hasattr(decl, 'span') and decl.span:
            label += f" [dim](line {decl.span.start_line})[/dim]"
            
        return label
    
    def _format_type(self, type_node):
        """Format a type node for display."""
        if hasattr(type_node, 'kind'):
            if type_node.kind.name == 'TYPE_PRIMITIVE':
                return type_node.type_name if hasattr(type_node, 'type_name') else 'primitive'
            elif type_node.kind.name == 'TYPE_ARRAY':
                elem_type = self._format_type(type_node.element_type) if hasattr(type_node, 'element_type') else '?'
                size = type_node.size if hasattr(type_node, 'size') else '?'
                return f"[{size}]{elem_type}"
            elif type_node.kind.name == 'TYPE_SLICE':
                elem_type = self._format_type(type_node.element_type) if hasattr(type_node, 'element_type') else '?'
                return f"[]{elem_type}"
            elif type_node.kind.name == 'TYPE_POINTER':
                target_type = self._format_type(type_node.target_type) if hasattr(type_node, 'target_type') else '?'
                return f"ref {target_type}"
        
        # Fallback for simple types or unknown structures
        if hasattr(type_node, 'type_name'):
            return type_node.type_name
        elif hasattr(type_node, 'name'):
            return type_node.name
        return str(type_node)
    
    def _add_statements_to_tree(self, parent_node, statements):
        """Add statement nodes to the tree."""
        for stmt in statements:
            stmt_label = f"[blue]{stmt.kind.name}[/blue]"
            
            # Add details based on statement type
            if hasattr(stmt, 'name') and stmt.name:
                stmt_label += f" [yellow]{stmt.name}[/yellow]"
            
            # For assignments, show target
            if hasattr(stmt, 'target') and hasattr(stmt.target, 'name') and stmt.target.name:
                stmt_label += f" [yellow]{stmt.target.name}[/yellow]"
                
            # For function calls, show function name
            if hasattr(stmt, 'function') and hasattr(stmt.function, 'name') and stmt.function.name:
                stmt_label += f" [yellow]{stmt.function.name}()[/yellow]"
            
            stmt_node = parent_node.add(stmt_label)
            
            # Recursively add nested statements for blocks and control flow
            if hasattr(stmt, 'statements') and stmt.statements:
                self._add_statements_to_tree(stmt_node, stmt.statements)
            elif hasattr(stmt, 'then_stmt') and stmt.then_stmt:
                if hasattr(stmt.then_stmt, 'statements'):
                    self._add_statements_to_tree(stmt_node, stmt.then_stmt.statements)
                if hasattr(stmt, 'else_stmt') and stmt.else_stmt:
                    if hasattr(stmt.else_stmt, 'statements'):
                        self._add_statements_to_tree(stmt_node, stmt.else_stmt.statements)
    
    def compile_file(self, input_path: str, output_path: Optional[str] = None) -> bool:
        """
        Compile a single A7 source file to the target backend.
        
        Args:
            input_path: Path to the .a7 source file
            output_path: Optional output path for the target file (auto-generated if None)
            
        Returns:
            True if compilation succeeded, False otherwise
        """
        try:
            # Validate input file
            if not os.path.exists(input_path):
                raise CompilerError(f"Input file not found: {input_path}")
            
            if not input_path.endswith('.a7'):
                raise CompilerError(f"Expected .a7 file, got: {input_path}")
            
            # Generate output path if not provided
            if output_path is None:
                output_path = self._generate_output_path(input_path)
            
            # Read source code
            with open(input_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            if self.verbose:
                print(f"Compiling {input_path} -> {output_path}")
            
            # Create error handler for this file
            error_handler = create_error_handler(input_path, source_code)
            
            # Compilation pipeline - tokenize and parse
            tokenizer = Tokenizer(source_code, filename=str(input_path))
            tokens = tokenizer.tokenize()
            
            # Parse tokens into AST (unless tokenize-only mode)
            ast = None
            if not self.tokenize_only:
                try:
                    source_lines = source_code.splitlines() if source_code else []
                    parser = Parser(tokens, filename=str(input_path), source_lines=source_lines)
                    ast = parser.parse()
                    
                    if self.verbose:
                        print(f"Successfully parsed {input_path}")
                except Exception as e:
                    if self.verbose:
                        print(f"Parse error in {input_path}: {e}")
                    # Continue with tokenization results even if parsing fails
            
            # Output results based on debug mode and format
            if self.json_output:
                # JSON output for debug modes
                json_result = self._compilation_to_json(tokens, ast, source_code, input_path)
                
                # Filter JSON output based on debug mode
                if self.tokenize_only:
                    # Only include tokenization data
                    filtered_result = {
                        "metadata": json_result["metadata"],
                        "source_code": json_result["source_code"], 
                        "tokens": json_result["tokens"],
                        "debug_mode": "tokenize_only"
                    }
                    print(json.dumps(filtered_result, indent=2))
                elif self.parse_only:
                    # Include tokenization and parsing data
                    filtered_result = {
                        "metadata": json_result["metadata"],
                        "source_code": json_result["source_code"],
                        "tokens": json_result["tokens"],
                        "ast": json_result["ast"],
                        "debug_mode": "parse_only"
                    }
                    print(json.dumps(filtered_result, indent=2))
                else:
                    # Full compilation data
                    json_result["debug_mode"] = "full_compilation"
                    print(json.dumps(json_result, indent=2))
            else:
                # Rich console output with debug modes
                self._display_debug_output(tokens, ast, source_code, input_path)
            # Skip actual code generation for now
            target_code = "// Tokenization complete - no code generation yet\n"
            
            # Write output (Skip for now)
            # os.makedirs(os.path.dirname(output_path), exist_ok=True)
            # with open(output_path, 'w', encoding='utf-8') as f:
            #     f.write(target_code)
            #
            # if self.verbose:
            #     print(f"Successfully compiled to {output_path}")
            
            return True
            
        except CompilerError as e:
            # Use Rich formatting to display error with source context
            if not self.json_output:
                from rich.console import Console
                console = Console()
                display_error(e, console)
            else:
                # In JSON mode, output error as JSON
                error_json = {
                    "error": {
                        "type": type(e).__name__,
                        "message": str(e),
                        "file": input_path
                    }
                }
                print(json.dumps(error_json, indent=2))
            return False
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return False
    
    def compile_project(self, project_root: str, output_dir: str = "build") -> bool:
        """
        Compile all .a7 files in a project directory.
        
        Args:
            project_root: Root directory containing A7 source files
            output_dir: Directory to place compiled target files
            
        Returns:
            True if all files compiled successfully, False otherwise
        """
        project_path = Path(project_root)
        if not project_path.exists():
            print(f"Project directory not found: {project_root}", file=sys.stderr)
            return False
        
        # Find all .a7 files
        a7_files = list(project_path.rglob("*.a7"))
        if not a7_files:
            print(f"No .a7 files found in {project_root}", file=sys.stderr)
            return False
        
        if self.verbose:
            print(f"Found {len(a7_files)} source files")
        
        success_count = 0
        for a7_file in a7_files:
            # Calculate relative output path
            rel_path = a7_file.relative_to(project_path)
            output_path = Path(output_dir) / rel_path.with_suffix('.zig')
            
            if self.compile_file(str(a7_file), str(output_path)):
                success_count += 1
        
        if success_count == len(a7_files):
            if self.verbose:
                print(f"Successfully compiled {success_count}/{len(a7_files)} files")
            return True
        else:
            print(f"Compilation failed: {success_count}/{len(a7_files)} files compiled", file=sys.stderr)
            return False
    
    def _generate_output_path(self, input_path: str) -> str:
        """Generate output path from input .a7 path."""
        return input_path.replace('.a7', '.zig')


def compile_a7_file(input_path: str, output_path: Optional[str] = None, verbose: bool = False, 
                   json_output: bool = False, tokenize_only: bool = False, parse_only: bool = False) -> bool:
    """
    Convenience function to compile a single A7 file.
    
    Args:
        input_path: Path to the .a7 source file
        output_path: Optional output path for the .zig file
        verbose: Enable verbose output
        json_output: Output compilation results in JSON format
        tokenize_only: Debug mode: only perform tokenization
        parse_only: Debug mode: only perform tokenization and parsing
        
    Returns:
        True if compilation succeeded, False otherwise
    """
    compiler = A7Compiler(verbose=verbose, json_output=json_output, 
                         tokenize_only=tokenize_only, parse_only=parse_only)
    return compiler.compile_file(input_path, output_path)


def compile_a7_project(project_root: str, output_dir: str = "build", verbose: bool = False) -> bool:
    """
    Convenience function to compile an A7 project.
    
    Args:
        project_root: Root directory containing A7 source files
        output_dir: Directory to place compiled .zig files
        verbose: Enable verbose output
        
    Returns:
        True if all files compiled successfully, False otherwise
    """
    compiler = A7Compiler(verbose=verbose)
    return compiler.compile_project(project_root, output_dir)
