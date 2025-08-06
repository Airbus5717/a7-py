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
    
    def __init__(self, backend: str = "zig", verbose: bool = False, json_output: bool = False):
        self.backend = backend
        self.verbose = verbose
        self.json_output = json_output
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
            
            # Parse tokens into AST
            ast = None
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
            
            # Output in JSON or Rich format based on flag
            if self.json_output:
                # JSON output
                json_result = self._compilation_to_json(tokens, ast, source_code, input_path)
                print(json.dumps(json_result, indent=2))
            else:
                # Rich console output
                from rich.console import Console
                from rich.table import Table
                from rich.text import Text
                
                console = Console()
                
                # Display source code
                code_panel = Panel(
                    source_code,
                    title=f"Source: {input_path}",
                    border_style="blue"
                )
                console.print(code_panel)
                
                # Display tokens
                token_table = Table(title="Tokens", show_header=True)
                token_table.add_column("Line", style="cyan", no_wrap=True)
                token_table.add_column("Column", style="magenta", no_wrap=True)
                token_table.add_column("Type", style="green")
                token_table.add_column("Value", style="yellow")
                
                for token in tokens:
                    token_table.add_row(
                        str(token.line),
                        str(token.column),
                        token.type.name,
                        repr(token.value) if token.value else ""
                    )
                
                console.print(token_table)
                
                # Display AST information
                if ast:
                    ast_text = Text("✅ Successfully parsed into AST", style="green bold")
                    console.print(ast_text)
                    
                    # Simple AST display
                    ast_info = Text()
                    ast_info.append("AST Root: ", style="bold")
                    ast_info.append(f"{ast.kind.name}", style="cyan")
                    if ast.declarations:
                        ast_info.append(f" ({len(ast.declarations)} declarations)", style="dim")
                    console.print(ast_info)
                else:
                    ast_text = Text("❌ Failed to parse AST", style="red bold")
                    console.print(ast_text)
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


def compile_a7_file(input_path: str, output_path: Optional[str] = None, verbose: bool = False, json_output: bool = False) -> bool:
    """
    Convenience function to compile a single A7 file.
    
    Args:
        input_path: Path to the .a7 source file
        output_path: Optional output path for the .zig file
        verbose: Enable verbose output
        json_output: Output compilation results in JSON format
        
    Returns:
        True if compilation succeeded, False otherwise
    """
    compiler = A7Compiler(verbose=verbose, json_output=json_output)
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
