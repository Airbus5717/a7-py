"""
Compiler error types and exception classes.
"""

from typing import Optional, Tuple


class CompilerError(Exception):
    """Base class for all compiler errors."""
    
    def __init__(self, message: str, location: Optional[Tuple[int, int]] = None, filename: Optional[str] = None):
        self.message = message
        self.location = location  # (line, column)
        self.filename = filename
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """Format the error message with location information."""
        parts = []
        
        if self.filename:
            parts.append(f"{self.filename}")
        
        if self.location:
            line, col = self.location
            parts.append(f"{line}:{col}")
        
        if parts:
            return f"{':'.join(parts)}: {self.message}"
        else:
            return self.message


class LexError(CompilerError):
    """Error during lexical analysis."""
    pass


class ParseError(CompilerError):
    """Error during parsing."""
    pass


class SemanticError(CompilerError):
    """Error during semantic analysis."""
    pass


class CodegenError(CompilerError):
    """Error during code generation."""
    pass


class ImportError(CompilerError):
    """Error resolving imports."""
    pass