"""
Compiler error types and exception classes with Rich formatting support.
"""

from typing import Optional, Tuple, List
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich import box


class LexErrorType(Enum):
    """Specific lexer error types with descriptive messages and advice."""
    OUT_OF_MEMORY = "out_of_memory"
    INVALID_CHARACTER = "invalid_character"
    TOO_LONG_IDENTIFIER = "too_long_identifier"
    TOO_LONG_NUMBER = "too_long_number"
    TOO_LONG_STRING = "too_long_string"
    NOT_CLOSED_CHAR = "not_closed_char"
    NOT_CLOSED_STRING = "not_closed_string"
    END_OF_FILE = "end_of_file"
    FILE_EMPTY = "file_empty"
    BAD_TOKEN_AT_GLOBAL = "bad_token_at_global"
    TABS_UNSUPPORTED = "tabs_unsupported"
    INVALID_ESCAPE_CHAR = "invalid_escape_char"
    NOT_CLOSED_COMMENT = "not_closed_comment"
    INVALID_SCIENTIFIC_NOTATION = "invalid_scientific_notation"
    INVALID_HEX_NUMBER = "invalid_hex_number"
    INVALID_BINARY_NUMBER = "invalid_binary_number"
    UNSUPPORTED = "unsupported"
    UNKNOWN = "unknown"


def get_lexer_error_message(error_type: LexErrorType) -> str:
    """Get the descriptive error message for a lexer error type."""
    messages = {
        LexErrorType.OUT_OF_MEMORY: "Out of memory",
        LexErrorType.INVALID_CHARACTER: "Invalid character",
        LexErrorType.TOO_LONG_IDENTIFIER: "Identifier is too long",
        LexErrorType.TOO_LONG_NUMBER: "Number is too long",
        LexErrorType.TOO_LONG_STRING: "String is too long",
        LexErrorType.NOT_CLOSED_CHAR: "The char is not closed",
        LexErrorType.NOT_CLOSED_STRING: "The string is not closed",
        LexErrorType.END_OF_FILE: "Reached end of file",
        LexErrorType.FILE_EMPTY: "The file is empty",
        LexErrorType.BAD_TOKEN_AT_GLOBAL: "Found global token at its forbidden scope",
        LexErrorType.TABS_UNSUPPORTED: "Tabs '\\t' are unsupported",
        LexErrorType.INVALID_ESCAPE_CHAR: "Invalid escaped char",
        LexErrorType.NOT_CLOSED_COMMENT: "Comment not closed",
        LexErrorType.INVALID_SCIENTIFIC_NOTATION: "Invalid scientific notation",
        LexErrorType.INVALID_HEX_NUMBER: "Invalid hexadecimal number",
        LexErrorType.INVALID_BINARY_NUMBER: "Invalid binary number",
        LexErrorType.UNSUPPORTED: "Unsupported feature",
        LexErrorType.UNKNOWN: "Unknown error"
    }
    return messages.get(error_type, "Unknown error")


def get_lexer_error_advice(error_type: LexErrorType) -> str:
    """Get helpful advice for fixing a lexer error."""
    advice = {
        LexErrorType.INVALID_ESCAPE_CHAR: "Change the letter after \\",
        LexErrorType.NOT_CLOSED_COMMENT: "Close the comment with delimiter",
        LexErrorType.INVALID_CHARACTER: "Remove this character",
        LexErrorType.OUT_OF_MEMORY: "The compiler needs more memory",
        LexErrorType.TOO_LONG_IDENTIFIER: "Identifier must not exceed 100 characters",
        LexErrorType.TOO_LONG_NUMBER: "Number must not exceed 100 digits",
        LexErrorType.TOO_LONG_STRING: "String must not exceed maximum length",
        LexErrorType.NOT_CLOSED_CHAR: "Close the char with a quote",
        LexErrorType.NOT_CLOSED_STRING: "Close the string with a double quote",
        LexErrorType.END_OF_FILE: "Needs more code for compiling",
        LexErrorType.FILE_EMPTY: "Do not compile empty files",
        LexErrorType.BAD_TOKEN_AT_GLOBAL: "Do not put this token in global scope",
        LexErrorType.TABS_UNSUPPORTED: "Convert the tabs to spaces",
        LexErrorType.INVALID_SCIENTIFIC_NOTATION: "Add digits after the exponent",
        LexErrorType.INVALID_HEX_NUMBER: "Use valid hexadecimal digits (0-9, a-f, A-F)",
        LexErrorType.INVALID_BINARY_NUMBER: "Use only binary digits (0, 1)",
        LexErrorType.UNSUPPORTED: "This feature is not yet supported",
        LexErrorType.UNKNOWN: "Please report this error"
    }
    return advice.get(error_type, "Please report this error")


@dataclass
class SourceSpan:
    """Represents a span of source code for error reporting."""
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    length: int = 0
    
    def __post_init__(self):
        if self.length == 0:
            # Calculate character length for single-line spans
            if self.start_line == self.end_line:
                self.length = self.end_column - self.start_column
            else:
                self.length = 1  # Multi-line spans default to 1


class ErrorFormatter:
    """Rich-based error formatter with source code context."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
    
    def format_error(self, error: 'CompilerError', context_lines: int = 2) -> None:
        """Format and display an error with source code context."""
        # Build the error message in format: "error: sentence, line: x, col: y"
        error_msg = Text()
        error_msg.append("error: ", style="red bold")
        error_msg.append(error.message, style="red")
        
        if error.span:
            error_msg.append(", line: ", style="red")
            error_msg.append(str(error.span.start_line), style="red bold")
            error_msg.append(", col: ", style="red")
            error_msg.append(str(error.span.start_column), style="red bold")
        
        self.console.print(error_msg)
        
        # Show advice if available (for LexError with error_type)
        if hasattr(error, 'error_type') and error.error_type:
            advice = get_lexer_error_advice(error.error_type)
            advice_msg = Text()
            advice_msg.append("help: ", style="cyan bold")
            advice_msg.append(advice, style="cyan")
            self.console.print(advice_msg)
        
        # Show source code context if available
        if error.source_lines and error.span:
            context_text = self._build_source_context(error.source_lines, error.span, context_lines)
            self.console.print(context_text)
    
    def _build_source_context(self, source_lines: List[str], span: SourceSpan, context_lines: int) -> Text:
        """Build syntax-highlighted source code context with error highlighting."""
        # For small files, ensure we show reasonable context
        total_lines = len(source_lines)
        
        if total_lines <= 5:
            # For very small files, show all lines
            start_show = 1
            end_show = total_lines
        else:
            # For larger files, use the requested context
            start_show = max(1, span.start_line - context_lines)
            end_show = min(total_lines, span.end_line + context_lines)
            
            # Ensure we show at least one line of context if possible
            if start_show == span.start_line and start_show > 1:
                start_show = max(1, start_show - 1)
            if end_show == span.end_line and end_show < total_lines:
                end_show = min(total_lines, end_show + 1)
        
        context_text = Text()
        
        for line_num in range(start_show, end_show + 1):
            line_content = source_lines[line_num - 1] if line_num <= len(source_lines) else ""
            line_num_str = f"{line_num:4d}"
            separator = " │ "
            
            # Yellow color for line numbers and separators
            context_text.append(line_num_str, style="yellow")
            context_text.append(separator, style="yellow")
            
            # Determine line styling
            if span.start_line <= line_num <= span.end_line:
                # This line contains the error
                if line_num == span.start_line == span.end_line:
                    # Single line error - highlight the exact span
                    before = line_content[:span.start_column]
                    error_part = line_content[span.start_column:span.end_column]
                    after = line_content[span.end_column:]
                    
                    # White/default color for code
                    context_text.append(before, style="white")
                    context_text.append(error_part, style="black on red")
                    context_text.append(after, style="white")
                else:
                    # Multi-line error
                    if line_num == span.start_line:
                        before = line_content[:span.start_column]
                        error_part = line_content[span.start_column:]
                        context_text.append(before, style="white")
                        context_text.append(error_part, style="black on red")
                    elif line_num == span.end_line:
                        error_part = line_content[:span.end_column]
                        after = line_content[span.end_column:]
                        context_text.append(error_part, style="black on red")
                        context_text.append(after, style="white")
                    else:
                        context_text.append(line_content, style="black on red")
                
                context_text.append("\n")
                
                # Add underline pointer line for single-line errors
                if line_num == span.start_line == span.end_line:
                    pointer_prefix = " " * 4 + " │ "
                    # Column is 1-based, so subtract 1 for 0-based spacing
                    pointer_spaces = " " * (span.start_column - 1)
                    underline = "^" * max(1, span.length)
                    
                    context_text.append(pointer_prefix, style="yellow")
                    context_text.append(pointer_spaces, style="white")
                    context_text.append(underline, style="red bold")
                    context_text.append("\n")
            else:
                # Context line - not part of error - white/default color for code
                context_text.append(line_content, style="white")
                context_text.append("\n")
        
        return context_text


class CompilerError(Exception):
    """Base class for all compiler errors with rich formatting support."""
    
    def __init__(
        self, 
        message: str, 
        span: Optional[SourceSpan] = None,
        filename: Optional[str] = None,
        source_lines: Optional[List[str]] = None
    ):
        self.message = message
        self.span = span
        self.filename = filename
        self.source_lines = source_lines or []
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """Format the error message with location information."""
        parts = []
        
        if self.filename:
            parts.append(f"{Path(self.filename).name}")
        
        if self.span:
            if self.span.start_line == self.span.end_line:
                parts.append(f"{self.span.start_line}:{self.span.start_column}")
            else:
                parts.append(f"{self.span.start_line}:{self.span.start_column}-{self.span.end_line}:{self.span.end_column}")
        
        if parts:
            return f"{':'.join(parts)}: {self.message}"
        else:
            return self.message
    
    def display(self, console: Optional[Console] = None, context_lines: int = 2) -> None:
        """Display this error with rich formatting and source context."""
        formatter = ErrorFormatter(console)
        formatter.format_error(self, context_lines)
    
    @classmethod
    def from_token(cls, message: str, token, filename: Optional[str] = None, source_lines: Optional[List[str]] = None):
        """Create an error from a token's location information."""
        span = SourceSpan(
            start_line=token.line,
            start_column=token.column,
            end_line=token.line,
            end_column=token.column + token.length,
            length=token.length
        )
        return cls(message, span, filename, source_lines)
    
    @classmethod
    def from_location(cls, message: str, line: int, column: int, length: int = 1, filename: Optional[str] = None, source_lines: Optional[List[str]] = None):
        """Create an error from explicit location information."""
        span = SourceSpan(
            start_line=line,
            start_column=column,
            end_line=line,
            end_column=column + length,
            length=length
        )
        return cls(message, span, filename, source_lines)


class LexError(CompilerError):
    """Error during lexical analysis."""
    
    def __init__(
        self,
        message: str,
        span: Optional[SourceSpan] = None,
        filename: Optional[str] = None,
        source_lines: Optional[List[str]] = None,
        error_type: Optional[LexErrorType] = None
    ):
        self.error_type = error_type
        super().__init__(message, span, filename, source_lines)
    
    @classmethod
    def from_type(
        cls,
        error_type: LexErrorType,
        span: Optional[SourceSpan] = None,
        filename: Optional[str] = None,
        source_lines: Optional[List[str]] = None,
        custom_message: Optional[str] = None
    ):
        """Create a LexError from an error type."""
        message = custom_message or get_lexer_error_message(error_type)
        return cls(message, span, filename, source_lines, error_type)
    
    @classmethod
    def from_type_and_location(
        cls,
        error_type: LexErrorType,
        line: int,
        column: int,
        length: int = 1,
        filename: Optional[str] = None,
        source_lines: Optional[List[str]] = None,
        custom_message: Optional[str] = None
    ):
        """Create a LexError from error type and location information."""
        span = SourceSpan(
            start_line=line,
            start_column=column,
            end_line=line,
            end_column=column + length,
            length=length
        )
        message = custom_message or get_lexer_error_message(error_type)
        return cls(message, span, filename, source_lines, error_type)


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


# Utility functions for error handling
def create_error_handler(filename: Optional[str] = None, source_code: Optional[str] = None):
    """Create a convenient error handler for a specific file."""
    source_lines = source_code.splitlines() if source_code else []
    
    class ErrorHandler:
        def __init__(self):
            self.filename = filename
            self.source_lines = source_lines
        
        def lex_error(self, message: str, line: int, column: int, length: int = 1) -> LexError:
            """Create a LexError with current file context."""
            return LexError.from_location(message, line, column, length, self.filename, self.source_lines)
        
        def parse_error(self, message: str, token=None, span: Optional[SourceSpan] = None) -> ParseError:
            """Create a ParseError with current file context."""
            if token:
                return ParseError.from_token(message, token, self.filename, self.source_lines)
            elif span:
                return ParseError(message, span, self.filename, self.source_lines)
            else:
                return ParseError(message, None, self.filename, self.source_lines)
        
        def semantic_error(self, message: str, token=None, span: Optional[SourceSpan] = None) -> SemanticError:
            """Create a SemanticError with current file context."""
            if token:
                return SemanticError.from_token(message, token, self.filename, self.source_lines)
            elif span:
                return SemanticError(message, span, self.filename, self.source_lines)
            else:
                return SemanticError(message, None, self.filename, self.source_lines)
        
        def codegen_error(self, message: str, token=None, span: Optional[SourceSpan] = None) -> CodegenError:
            """Create a CodegenError with current file context."""
            if token:
                return CodegenError.from_token(message, token, self.filename, self.source_lines)
            elif span:
                return CodegenError(message, span, self.filename, self.source_lines)
            else:
                return CodegenError(message, None, self.filename, self.source_lines)
    
    return ErrorHandler()


def display_error(error: CompilerError, console: Optional[Console] = None, context_lines: int = 2):
    """Convenience function to display any compiler error with rich formatting."""
    error.display(console, context_lines)


def create_span_between_tokens(start_token, end_token) -> SourceSpan:
    """Create a SourceSpan that covers from start_token to end_token."""
    return SourceSpan(
        start_line=start_token.line,
        start_column=start_token.column,
        end_line=end_token.line,
        end_column=end_token.column + end_token.length
    )


def create_span_from_tokens(tokens: List) -> SourceSpan:
    """Create a SourceSpan that covers all the given tokens."""
    if not tokens:
        raise ValueError("Cannot create span from empty token list")
    
    first_token = tokens[0]
    last_token = tokens[-1]
    
    return create_span_between_tokens(first_token, last_token)