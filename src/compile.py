"""
A7 to Zig Compiler

Main compilation pipeline that orchestrates lexing, parsing, and code generation.
"""

import os
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
            
console = Console()
from .tokens import Tokenizer
# from .parser import Parser  # Not yet implemented
# from .backends import get_backend  # Ignoring backend for now
from .errors import CompilerError


class A7Compiler:
    """Main compiler class that handles the A7 compilation pipeline with pluggable backends."""
    
    def __init__(self, backend: str = "zig", verbose: bool = False):
        self.backend = backend
        self.verbose = verbose
        # Tokenizer will be created per file during compilation
        # self.parser = Parser()  # Not yet implemented
        # self.codegen = get_backend(backend)  # Ignoring backend for now
    
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
            
            # Compilation pipeline - just tokenize and log output
            from rich.console import Console
            from rich.table import Table
            
            console = Console()
            tokenizer = Tokenizer(source_code)
            tokens = tokenizer.tokenize()
            
            # Display tokens using Rich
            table = Table(title=f"Tokens for {input_path}")
            table.add_column("Line", style="cyan", no_wrap=True)
            table.add_column("Column", style="magenta", no_wrap=True)
            table.add_column("Type", style="green")
            table.add_column("Value", style="yellow")
            
            for token in tokens:
                table.add_row(
                    str(token.line),
                    str(token.column),
                    token.type.name,
                    repr(token.value) if token.value else ""
                )
            
            code_panel = Panel(
                source_code,
                title=f"Source: {input_path}",
                border_style="blue"
            )
            console.print(code_panel)
            console.print(table)
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
            print(f"Compilation error: {e}", file=sys.stderr)
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


def compile_a7_file(input_path: str, output_path: Optional[str] = None, verbose: bool = False) -> bool:
    """
    Convenience function to compile a single A7 file.
    
    Args:
        input_path: Path to the .a7 source file
        output_path: Optional output path for the .zig file
        verbose: Enable verbose output
        
    Returns:
        True if compilation succeeded, False otherwise
    """
    compiler = A7Compiler(verbose=verbose)
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
