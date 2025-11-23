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

# Semantic analysis passes
from .passes import NameResolutionPass, TypeCheckingPass, SemanticValidationPass
from .errors import (
    CompilerError, SemanticError, TypeCheckError,
    display_error, display_errors, create_error_handler,
    SemanticErrorType, TypeErrorType
)

# Output formatters
from .formatters import JSONFormatter, ConsoleFormatter


class A7Compiler:
    """Main compiler class that handles the A7 compilation pipeline with pluggable backends."""

    def __init__(
        self,
        backend: str = "zig",
        verbose: bool = False,
        json_output: bool = False,
        tokenize_only: bool = False,
        parse_only: bool = False,
    ):
        self.backend = backend
        self.verbose = verbose
        self.json_output = json_output
        self.tokenize_only = tokenize_only
        self.parse_only = parse_only
        # Tokenizer will be created per file during compilation
        # self.parser = Parser()  # Not yet implemented
        # self.codegen = get_backend(backend)  # Ignoring backend for now

        # Initialize formatters
        self.json_formatter = JSONFormatter(backend=backend)
        self.console_formatter = ConsoleFormatter(
            tokenize_only=tokenize_only,
            parse_only=parse_only
        )

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

            if not input_path.endswith(".a7"):
                raise CompilerError(f"Expected .a7 file, got: {input_path}")

            # Generate output path if not provided
            if output_path is None:
                output_path = self._generate_output_path(input_path)

            # Read source code
            with open(input_path, "r", encoding="utf-8") as f:
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
                    parser = Parser(
                        tokens, filename=str(input_path), source_lines=source_lines
                    )
                    ast = parser.parse()

                    if self.verbose:
                        print(f"Successfully parsed {input_path}")
                except Exception as e:
                    if self.verbose:
                        print(f"Parse error in {input_path}: {e}")
                    # Continue with tokenization results even if parsing fails

            # Semantic analysis (unless in parse-only or tokenize-only mode)
            if ast and not self.tokenize_only and not self.parse_only:
                if self.verbose:
                    print(f"Running semantic analysis on {input_path}...")

                all_errors = []
                source_lines = source_code.splitlines() if source_code else []

                # Pass 1: Name resolution
                name_resolver = NameResolutionPass()
                name_resolver.source_lines = source_lines
                symbol_table = name_resolver.analyze(ast, str(input_path))

                if name_resolver.errors:
                    all_errors.extend(name_resolver.errors)
                    if self.verbose:
                        print(f"  ✗ Name resolution: {len(name_resolver.errors)} error(s)")
                elif self.verbose:
                    print(f"  ✓ Name resolution complete")

                # Pass 2: Type checking (only if name resolution succeeded)
                if not name_resolver.errors:
                    type_checker = TypeCheckingPass(symbol_table)
                    type_checker.source_lines = source_lines
                    type_checker.analyze(ast, str(input_path))

                    if type_checker.errors:
                        all_errors.extend(type_checker.errors)
                        if self.verbose:
                            print(f"  ✗ Type checking: {len(type_checker.errors)} error(s)")
                    elif self.verbose:
                        print(f"  ✓ Type checking complete")

                    # Pass 3: Semantic validation (only if type checking succeeded)
                    if not type_checker.errors:
                        validator = SemanticValidationPass(symbol_table, type_checker.node_types)
                        validator.source_lines = source_lines
                        validator.analyze(ast, str(input_path))

                        if validator.errors:
                            all_errors.extend(validator.errors)
                            if self.verbose:
                                print(f"  ✗ Semantic validation: {len(validator.errors)} error(s)")
                        elif self.verbose:
                            print(f"  ✓ Semantic validation complete")
                            print(f"Successfully analyzed {input_path}")

                # If there are semantic errors, display them all
                if all_errors:
                    from rich.console import Console
                    console = Console()
                    display_errors(all_errors, console)
                    return False

            # Output results based on debug mode and format
            if self.json_output:
                # JSON output using formatter
                json_result = self.json_formatter.format_compilation(
                    tokens, ast, source_code, input_path
                )

                # Filter JSON output based on debug mode
                if self.tokenize_only:
                    # Only include tokenization data
                    filtered_result = {
                        "metadata": json_result["metadata"],
                        "source_code": json_result["source_code"],
                        "tokens": json_result["tokens"],
                        "debug_mode": "tokenize_only",
                    }
                    print(json.dumps(filtered_result, indent=2))
                elif self.parse_only:
                    # Include tokenization and parsing data
                    filtered_result = {
                        "metadata": json_result["metadata"],
                        "source_code": json_result["source_code"],
                        "tokens": json_result["tokens"],
                        "ast": json_result["ast"],
                        "debug_mode": "parse_only",
                    }
                    print(json.dumps(filtered_result, indent=2))
                else:
                    # Full compilation data
                    json_result["debug_mode"] = "full_compilation"
                    print(json.dumps(json_result, indent=2))
            else:
                # Rich console output using formatter
                self.console_formatter.display_compilation(
                    tokens, ast, source_code, input_path
                )
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
                        "file": input_path,
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
            output_path = Path(output_dir) / rel_path.with_suffix(".zig")

            if self.compile_file(str(a7_file), str(output_path)):
                success_count += 1

        if success_count == len(a7_files):
            if self.verbose:
                print(f"Successfully compiled {success_count}/{len(a7_files)} files")
            return True
        else:
            print(
                f"Compilation failed: {success_count}/{len(a7_files)} files compiled",
                file=sys.stderr,
            )
            return False

    def _generate_output_path(self, input_path: str) -> str:
        """Generate output path from input .a7 path."""
        return input_path.replace(".a7", ".zig")


def compile_a7_file(
    input_path: str,
    output_path: Optional[str] = None,
    verbose: bool = False,
    json_output: bool = False,
    tokenize_only: bool = False,
    parse_only: bool = False,
) -> bool:
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
    compiler = A7Compiler(
        verbose=verbose,
        json_output=json_output,
        tokenize_only=tokenize_only,
        parse_only=parse_only,
    )
    return compiler.compile_file(input_path, output_path)


def compile_a7_project(
    project_root: str, output_dir: str = "build", verbose: bool = False
) -> bool:
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
