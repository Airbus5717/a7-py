"""
Token types and tokenizer for the A7 programming language.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, List, Union
import re
import string


class TokenType(Enum):
    # Literals
    INTEGER_LITERAL = auto()
    FLOAT_LITERAL = auto()
    STRING_LITERAL = auto()
    CHAR_LITERAL = auto()
    TRUE_LITERAL = auto()
    FALSE_LITERAL = auto()
    NIL_LITERAL = auto()
    
    # Identifiers and Keywords
    IDENTIFIER = auto()
    BUILTIN_ID = auto()  # @function
    
    # Keywords
    AND = auto()         # and
    AS = auto()          # as
    BOOL = auto()        # bool
    BREAK = auto()       # break
    CASE = auto()        # case
    CHAR = auto()        # char
    CONTINUE = auto()    # continue
    DEL = auto()         # del (delete)
    DEFER = auto()       # defer
    ELSE = auto()        # else
    ENUM = auto()        # enum
    FALL = auto()        # fall
    FALSE = auto()       # false
    FLOAT = auto()       # float
    FN = auto()          # fn
    FOR = auto()         # for
    IF = auto()          # if
    IMPORT = auto()      # import
    IN = auto()          # in
    INT = auto()         # int
    I8 = auto()          # i8
    I16 = auto()         # i16
    I32 = auto()         # i32
    I64 = auto()         # i64
    ISIZE = auto()       # isize
    LET = auto()         # let
    MATCH = auto()       # match
    NEW = auto()         # new
    NIL = auto()         # nil
    NOT = auto()         # not
    OR = auto()          # or
    PUB = auto()         # pub
    REF = auto()         # ref
    RET = auto()         # ret
    STRING = auto()      # string
    STRUCT = auto()      # struct
    TRUE = auto()        # true
    U8 = auto()          # u8
    U16 = auto()         # u16
    U32 = auto()         # u32
    U64 = auto()         # u64
    UINT = auto()        # uint
    USIZE = auto()       # usize
    WHILE = auto()       # while
    
    # Operators
    PLUS = auto()            # +
    MINUS = auto()           # -
    MULTIPLY = auto()        # *
    DIVIDE = auto()          # /
    MODULO = auto()          # %
    
    # Assignment operators
    ASSIGN = auto()          # =
    PLUS_ASSIGN = auto()     # +=
    MINUS_ASSIGN = auto()    # -=
    MULTIPLY_ASSIGN = auto() # *=
    DIVIDE_ASSIGN = auto()   # /=
    MODULO_ASSIGN = auto()   # %=
    
    # Comparison operators
    EQUAL = auto()           # ==
    NOT_EQUAL = auto()       # !=
    LESS_THAN = auto()       # <
    LESS_EQUAL = auto()      # <=
    GREATER_THAN = auto()    # >
    GREATER_EQUAL = auto()   # >=
    
    # Bitwise operators
    BITWISE_AND = auto()     # &
    BITWISE_OR = auto()      # |
    BITWISE_XOR = auto()     # ^
    BITWISE_NOT = auto()     # ~
    LEFT_SHIFT = auto()      # <<
    RIGHT_SHIFT = auto()     # >>
    
    # Bitwise assignment operators
    BITWISE_AND_ASSIGN = auto()  # &=
    BITWISE_OR_ASSIGN = auto()   # |=
    BITWISE_XOR_ASSIGN = auto()  # ^=
    LEFT_SHIFT_ASSIGN = auto()   # <<=
    RIGHT_SHIFT_ASSIGN = auto()  # >>=
    
    # Logical operators (handled as keywords)
    LOGICAL_NOT = auto()     # !
    
    # Punctuation
    SEMICOLON = auto()       # ;
    COLON = auto()           # :
    COMMA = auto()           # ,
    DOT = auto()             # .
    DOT_DOT = auto()         # ..
    
    # Declaration operators
    DECLARE_CONST = auto()   # ::
    DECLARE_VAR = auto()     # :=
    
    # Brackets and Parentheses
    LEFT_PAREN = auto()      # (
    RIGHT_PAREN = auto()     # )
    LEFT_BRACKET = auto()    # [
    RIGHT_BRACKET = auto()   # ]
    LEFT_BRACE = auto()      # {
    RIGHT_BRACE = auto()     # }
    
    # Pointer operators
    ADDRESS_OF = auto()      # &
    DEREFERENCE = auto()     # ptr.* (handled specially)
    
    # Comments
    COMMENT = auto()         # // or /* */
    
    # Special tokens
    NEWLINE = auto()         # \n (significant in A7)
    EOF = auto()             # End of file
    TERMINATOR = auto()      # Statement terminator


@dataclass
class Token:
    """Represents a single token in the A7 language."""
    type: TokenType
    value: str
    line: int
    column: int
    length: int = 0
    
    def __post_init__(self):
        if self.length == 0:
            self.length = len(self.value)


class LexerError(Exception):
    """Exception raised for lexical analysis errors."""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer error at line {line}, column {column}: {message}")


class Tokenizer:
    """Tokenizes A7 source code into tokens."""
    
    # Keywords mapping
    KEYWORDS = {
        'and': TokenType.AND,
        'as': TokenType.AS,
        'bool': TokenType.BOOL,
        'break': TokenType.BREAK,
        'case': TokenType.CASE,
        'char': TokenType.CHAR,
        'continue': TokenType.CONTINUE,
        'del': TokenType.DEL,
        'defer': TokenType.DEFER,
        'else': TokenType.ELSE,
        'enum': TokenType.ENUM,
        'fall': TokenType.FALL,
        'false': TokenType.FALSE,
        'float': TokenType.FLOAT,
        'fn': TokenType.FN,
        'for': TokenType.FOR,
        'if': TokenType.IF,
        'import': TokenType.IMPORT,
        'in': TokenType.IN,
        'int': TokenType.INT,
        'i8': TokenType.I8,
        'i16': TokenType.I16,
        'i32': TokenType.I32,
        'i64': TokenType.I64,
        'isize': TokenType.ISIZE,
        'let': TokenType.LET,
        'match': TokenType.MATCH,
        'new': TokenType.NEW,
        'nil': TokenType.NIL,
        'not': TokenType.NOT,
        'or': TokenType.OR,
        'pub': TokenType.PUB,
        'ref': TokenType.REF,
        'ret': TokenType.RET,
        'string': TokenType.STRING,
        'struct': TokenType.STRUCT,
        'true': TokenType.TRUE,
        'u8': TokenType.U8,
        'u16': TokenType.U16,
        'u32': TokenType.U32,
        'u64': TokenType.U64,
        'uint': TokenType.UINT,
        'usize': TokenType.USIZE,
        'while': TokenType.WHILE,
    }
    
    def __init__(self, source_code: str):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        
    def current_char(self) -> Optional[str]:
        """Get the current character at position."""
        if self.position >= len(self.source):
            return None
        return self.source[self.position]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Peek at character at current position + offset."""
        pos = self.position + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]
    
    def advance(self) -> Optional[str]:
        """Advance position and return the current character."""
        if self.position >= len(self.source):
            return None
        
        char = self.source[self.position]
        self.position += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
            
        return char
    
    def skip_whitespace(self):
        """Skip whitespace characters except newlines."""
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def tokenize(self) -> List[Token]:
        """Tokenize the source code and return list of tokens."""
        while self.position < len(self.source):
            self.skip_whitespace()
            
            if self.current_char() is None:
                break
                
            # Handle newlines (significant in A7)
            if self.current_char() == '\n':
                self._add_token(TokenType.NEWLINE, '\n')
                self.advance()
                continue
            
            # Handle comments
            if self._try_comment():
                continue
                
            # Handle numbers
            if self.current_char() and self.current_char().isdigit():
                self._tokenize_number()
                continue
            
            # Handle strings
            if self.current_char() == '"':
                self._tokenize_string()
                continue
                
            # Handle character literals
            if self.current_char() == "'":
                self._tokenize_char()
                continue
            
            # Handle identifiers and keywords
            if self.current_char() and (self.current_char().isalpha() or self.current_char() == '_'):
                self._tokenize_identifier()
                continue
            
            # Handle builtin functions (@function)
            if self.current_char() == '@':
                self._tokenize_builtin()
                continue
            
            # Handle operators and punctuation
            if self._try_operator():
                continue
            
            # Unknown character
            raise LexerError(f"Unexpected character: '{self.current_char()}'", self.line, self.column)
        
        # Add EOF token
        self._add_token(TokenType.EOF, '')
        return self.tokens
    
    def _add_token(self, token_type: TokenType, value: str):
        """Add a token to the tokens list."""
        token = Token(token_type, value, self.line, self.column - len(value))
        self.tokens.append(token)
    
    def _try_comment(self) -> bool:
        """Try to tokenize a comment. Returns True if successful."""
        if self.current_char() == '/' and self.peek_char() == '/':
            # Single line comment
            start_pos = self.position
            while self.current_char() and self.current_char() != '\n':
                self.advance()
            comment_text = self.source[start_pos:self.position]
            self._add_token(TokenType.COMMENT, comment_text)
            return True
        
        if self.current_char() == '/' and self.peek_char() == '*':
            # Multi-line comment
            start_pos = self.position
            self.advance()  # /
            self.advance()  # *
            
            depth = 1
            while self.current_char() and depth > 0:
                if self.current_char() == '/' and self.peek_char() == '*':
                    self.advance()
                    self.advance()
                    depth += 1
                elif self.current_char() == '*' and self.peek_char() == '/':
                    self.advance()
                    self.advance()
                    depth -= 1
                else:
                    self.advance()
            
            comment_text = self.source[start_pos:self.position]
            self._add_token(TokenType.COMMENT, comment_text)
            return True
        
        if self.current_char() == '#':
            # Alternative single line comment
            start_pos = self.position
            while self.current_char() and self.current_char() != '\n':
                self.advance()
            comment_text = self.source[start_pos:self.position]
            self._add_token(TokenType.COMMENT, comment_text)
            return True
        
        return False
    
    def _tokenize_number(self):
        """Tokenize integer or float literals."""
        start_pos = self.position
        is_float = False
        
        # Handle binary numbers (0b)
        if self.current_char() == '0' and self.peek_char() == 'b':
            self.advance()  # 0
            self.advance()  # b
            while self.current_char() and self.current_char() in '01':
                self.advance()
            number_text = self.source[start_pos:self.position]
            self._add_token(TokenType.INTEGER_LITERAL, number_text)
            return
        
        # Handle hexadecimal numbers (0x)
        if self.current_char() == '0' and self.peek_char() == 'x':
            self.advance()  # 0
            self.advance()  # x
            while self.current_char() and self.current_char() in '0123456789abcdefABCDEF':
                self.advance()
            number_text = self.source[start_pos:self.position]
            self._add_token(TokenType.INTEGER_LITERAL, number_text)
            return
        
        # Handle decimal numbers
        while self.current_char() and self.current_char().isdigit():
            self.advance()
        
        # Check for decimal point (but not range operator ..)
        if self.current_char() == '.' and self.peek_char() != '.':
            is_float = True
            self.advance()  # .
            while self.current_char() and self.current_char().isdigit():
                self.advance()
        
        # Check for scientific notation (e or E followed by optional +/- and digits)
        if self.current_char() and self.current_char() in 'eE':
            is_float = True
            self.advance()  # e or E
            
            # Optional + or - after e/E
            if self.current_char() and self.current_char() in '+-':
                self.advance()
            
            # Must have at least one digit after e/E (and optional +/-)
            if not (self.current_char() and self.current_char().isdigit()):
                raise LexerError("Invalid scientific notation: missing exponent digits", self.line, self.column)
            
            # Parse exponent digits
            while self.current_char() and self.current_char().isdigit():
                self.advance()
        
        number_text = self.source[start_pos:self.position]
        token_type = TokenType.FLOAT_LITERAL if is_float else TokenType.INTEGER_LITERAL
        self._add_token(token_type, number_text)
    
    def _tokenize_string(self):
        """Tokenize string literals."""
        start_pos = self.position
        self.advance()  # Opening quote
        
        while self.current_char() and self.current_char() != '"':
            if self.current_char() == '\\':
                self.advance()  # Escape character
                if self.current_char():
                    self.advance()  # Escaped character
            else:
                self.advance()
        
        if not self.current_char():
            raise LexerError("Unterminated string literal", self.line, self.column)
        
        self.advance()  # Closing quote
        string_text = self.source[start_pos:self.position]
        self._add_token(TokenType.STRING_LITERAL, string_text)
    
    def _tokenize_char(self):
        """Tokenize character literals."""
        start_pos = self.position
        self.advance()  # Opening quote
        
        if self.current_char() == '\\':
            self.advance()  # Escape character
            if self.current_char():
                self.advance()  # Escaped character
        elif self.current_char():
            self.advance()  # Single character
        
        if self.current_char() != "'":
            raise LexerError("Unterminated or invalid character literal", self.line, self.column)
        
        self.advance()  # Closing quote
        char_text = self.source[start_pos:self.position]
        self._add_token(TokenType.CHAR_LITERAL, char_text)
    
    def _tokenize_identifier(self):
        """Tokenize identifiers and keywords."""
        start_pos = self.position
        
        while (self.current_char() and 
               (self.current_char().isalnum() or self.current_char() == '_')):
            self.advance()
        
        identifier_text = self.source[start_pos:self.position]
        
        # Check if it's a keyword
        token_type = self.KEYWORDS.get(identifier_text, TokenType.IDENTIFIER)
        
        # Handle boolean literals
        if identifier_text == 'true':
            token_type = TokenType.TRUE_LITERAL
        elif identifier_text == 'false':
            token_type = TokenType.FALSE_LITERAL
        elif identifier_text == 'nil':
            token_type = TokenType.NIL_LITERAL
        
        self._add_token(token_type, identifier_text)
    
    def _tokenize_builtin(self):
        """Tokenize builtin function identifiers (@function)."""
        start_pos = self.position
        self.advance()  # @
        
        while self.current_char() and self.current_char().isalpha():
            self.advance()
        
        builtin_text = self.source[start_pos:self.position]
        self._add_token(TokenType.BUILTIN_ID, builtin_text)
    
    def _try_operator(self) -> bool:
        """Try to tokenize operators and punctuation. Returns True if successful."""
        char = self.current_char()
        next_char = self.peek_char()
        
        # Three-character operators (check these first!)
        if char == '<' and next_char == '<' and self.peek_char(2) == '=':
            self._add_token(TokenType.LEFT_SHIFT_ASSIGN, '<<=')
            self.advance()
            self.advance()
            self.advance()
            return True
        elif char == '>' and next_char == '>' and self.peek_char(2) == '=':
            self._add_token(TokenType.RIGHT_SHIFT_ASSIGN, '>>=')
            self.advance()
            self.advance()
            self.advance()
            return True
        
        # Two-character operators
        two_char = char + (next_char or '')
        
        if two_char == '::':
            self._add_token(TokenType.DECLARE_CONST, '::')
            self.advance()
            self.advance()
            return True
        elif two_char == ':=':
            self._add_token(TokenType.DECLARE_VAR, ':=')
            self.advance()
            self.advance()
            return True
        elif two_char == '==':
            self._add_token(TokenType.EQUAL, '==')
            self.advance()
            self.advance()
            return True
        elif two_char == '!=':
            self._add_token(TokenType.NOT_EQUAL, '!=')
            self.advance()
            self.advance()
            return True
        elif two_char == '<=':
            self._add_token(TokenType.LESS_EQUAL, '<=')
            self.advance()
            self.advance()
            return True
        elif two_char == '>=':
            self._add_token(TokenType.GREATER_EQUAL, '>=')
            self.advance()
            self.advance()
            return True
        elif two_char == '<<':
            self._add_token(TokenType.LEFT_SHIFT, '<<')
            self.advance()
            self.advance()
            return True
        elif two_char == '>>':
            self._add_token(TokenType.RIGHT_SHIFT, '>>')
            self.advance()
            self.advance()
            return True
        elif two_char == '+=':
            self._add_token(TokenType.PLUS_ASSIGN, '+=')
            self.advance()
            self.advance()
            return True
        elif two_char == '-=':
            self._add_token(TokenType.MINUS_ASSIGN, '-=')
            self.advance()
            self.advance()
            return True
        elif two_char == '*=':
            self._add_token(TokenType.MULTIPLY_ASSIGN, '*=')
            self.advance()
            self.advance()
            return True
        elif two_char == '/=':
            self._add_token(TokenType.DIVIDE_ASSIGN, '/=')
            self.advance()
            self.advance()
            return True
        elif two_char == '%=':
            self._add_token(TokenType.MODULO_ASSIGN, '%=')
            self.advance()
            self.advance()
            return True
        elif two_char == '&=':
            self._add_token(TokenType.BITWISE_AND_ASSIGN, '&=')
            self.advance()
            self.advance()
            return True
        elif two_char == '|=':
            self._add_token(TokenType.BITWISE_OR_ASSIGN, '|=')
            self.advance()
            self.advance()
            return True
        elif two_char == '^=':
            self._add_token(TokenType.BITWISE_XOR_ASSIGN, '^=')
            self.advance()
            self.advance()
            return True
        elif two_char == '..':
            self._add_token(TokenType.DOT_DOT, '..')
            self.advance()
            self.advance()
            return True
        
        # Single-character operators
        operators = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '%': TokenType.MODULO,
            '=': TokenType.ASSIGN,
            '<': TokenType.LESS_THAN,
            '>': TokenType.GREATER_THAN,
            '&': TokenType.BITWISE_AND,  # Also ADDRESS_OF, context-dependent
            '|': TokenType.BITWISE_OR,
            '^': TokenType.BITWISE_XOR,
            '~': TokenType.BITWISE_NOT,
            '!': TokenType.LOGICAL_NOT,
            ';': TokenType.SEMICOLON,
            ':': TokenType.COLON,
            ',': TokenType.COMMA,
            '.': TokenType.DOT,
            '(': TokenType.LEFT_PAREN,
            ')': TokenType.RIGHT_PAREN,
            '[': TokenType.LEFT_BRACKET,
            ']': TokenType.RIGHT_BRACKET,
            '{': TokenType.LEFT_BRACE,
            '}': TokenType.RIGHT_BRACE,
        }
        
        if char in operators:
            self._add_token(operators[char], char)
            self.advance()
            return True
        
        return False
