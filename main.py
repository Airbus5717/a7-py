#!/usr/bin/env uv run python
# -*- coding: utf-8 -*-

import sys
import argparse
from pathlib import Path
from src.compile import compile_a7_file


def main():
    parser = argparse.ArgumentParser(
        description="A7 Programming Language Compiler/Interpreter",
        prog="a7-py"
    )
    
    parser.add_argument(
        "file",
        nargs="?",
        help="A7 source file (.a7) to compile"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: auto-generated)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    if not args.file:
        print("Usage: python main.py <file.a7> [-o output] [-v]")
        return
    
    # Validate input file
    input_path = Path(args.file)
    if not input_path.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    if not input_path.suffix == ".a7":
        print(f"Error: Expected .a7 file, got: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    # Compile the file
    success = compile_a7_file(
        str(input_path),
        args.output,
        verbose=args.verbose
    )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
