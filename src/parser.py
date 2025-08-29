"""
Recursive descent parser for the A7 programming language.

This parser implements the A7 grammar as specified in docs/SPEC.md section 12.
It uses a simple recursive descent approach with precedence climbing for expressions.
"""

from typing import List, Optional, Union
from .tokens import Token, TokenType, Tokenizer
from .ast_nodes import (
    ASTNode,
    NodeKind,
    LiteralKind,
    BinaryOp,
    UnaryOp,
    AssignOp,
    create_program,
    create_literal,
    create_identifier,
    create_binary_expr,
    create_function_decl,
    create_primitive_type,
    create_block,
    create_parameter,
    create_return_stmt,
    create_call_expr,
    create_assignment_stmt,
    create_var_decl,
    create_const_decl,
    create_cast_expr,
    create_literal_from_token,
    create_span_from_token,
    create_span_from_tokens,
    token_to_binary_op,
    token_to_unary_op,
    token_to_assign_op,
    get_binary_precedence,
)
from .errors import ParseError, SourceSpan, create_span_between_tokens


class Parser:
    """Recursive descent parser for A7."""

    def __init__(
        self,
        tokens: List[Token],
        filename: Optional[str] = None,
        source_lines: Optional[List[str]] = None,
    ):
        self.tokens = tokens
        self.filename = filename
        self.source_lines = source_lines or []
        self.position = 0
        self.current_token = self.tokens[0] if tokens else None

        # Skip to first non-terminator token
        self.skip_terminators()

    def current(self) -> Token:
        """Get current token."""
        if self.position >= len(self.tokens):
            return self.tokens[-1]  # Return EOF token
        return self.tokens[self.position]

    def peek(self, offset: int = 1) -> Token:
        """Peek at token at current position + offset."""
        pos = self.position + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]  # Return EOF token
        return self.tokens[pos]

    def advance(self) -> Token:
        """Advance to next token and return the previous one."""
        prev = self.current()
        if self.position < len(self.tokens) - 1:
            self.position += 1
        return prev

    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        return self.current().type in token_types

    def consume(self, token_type: TokenType, message: str = None) -> Token:
        """Consume a token of the expected type or raise an error."""
        if not self.match(token_type):
            if message is None:
                message = f"Expected {token_type.name}, got {self.current().type.name}"
            raise ParseError.from_token(
                message, self.current(), self.filename, self.source_lines
            )
        return self.advance()

    def skip_terminators(self):
        """Skip newline and semicolon terminators."""
        while self.match(TokenType.TERMINATOR):
            self.advance()

    def at_end(self) -> bool:
        """Check if we're at the end of input."""
        return self.match(TokenType.EOF)

    def _should_parse_struct_literal(self) -> bool:
        """
        Determine if we should parse identifier{ as a struct literal.

        Returns False if we're likely in a statement context where { starts a block,
        such as in if conditions, while conditions, etc.
        """
        # For now, use a simple heuristic: if we see common statement keywords
        # in recent tokens, we're likely in a statement context

        # Look back a few tokens to see if we're in a statement context  
        # Use a larger lookback distance to handle complex for loop syntax like "for i, value in arr"
        lookback_distance = min(8, self.position)
        for i in range(1, lookback_distance + 1):
            if self.position - i >= 0:
                prev_token = self.tokens[self.position - i]
                if prev_token.type in (
                    TokenType.IF,
                    TokenType.WHILE,
                    TokenType.FOR,
                    TokenType.MATCH,
                    TokenType.ELSE,
                ):
                    return False

        # Default to allowing struct literals
        return True

    def parse(self) -> ASTNode:
        """Parse the entire program."""
        declarations = []

        self.skip_terminators()

        # Safety mechanism to prevent infinite loops
        max_iterations = 1000
        iteration_count = 0

        while not self.at_end() and iteration_count < max_iterations:
            iteration_count += 1
            prev_position = self.position

            try:
                decl = self.parse_declaration()
                if decl:
                    declarations.append(decl)
                self.skip_terminators()

                # Ensure we're making progress
                if self.position <= prev_position and not self.at_end():
                    # Force advancement if we're stuck
                    self.advance()

            except ParseError as e:
                # If no complete declarations have been parsed, re-raise the error
                # This ensures malformed syntax raises proper errors
                if len(declarations) == 0:
                    raise e

                # Check for specific error patterns that should not be recovered from
                error_msg = str(e)
                
                # Case 1: Single declaration with unexpected tokens after complete program
                if len(declarations) == 1 and "Expected declaration" in error_msg:
                    current_token = self.current()
                    raise ParseError.from_token(
                        f"Unexpected token '{current_token.value}' after parsing complete program",
                        current_token, self.filename
                    )
                
                # Case 2: Incomplete expressions (missing operand after operator) 
                if "Expected expression after" in error_msg:
                    # These are syntax errors that shouldn't be recovered from
                    raise e

                # Otherwise do error recovery for multi-declaration programs
                self.synchronize()

                # Ensure we're making progress after error recovery
                if self.position <= prev_position and not self.at_end():
                    # Force advancement if synchronization didn't help
                    self.advance()

        if iteration_count >= max_iterations:
            # Log warning but don't crash
            if hasattr(self, "filename") and self.filename:
                print(
                    f"Warning: Parser stopped after {max_iterations} iterations in {self.filename}"
                )

        # Check if there are unparsed tokens remaining
        if not self.at_end():
            current_token = self.current()
            raise ParseError.from_token(
                f"Unexpected token '{current_token.value}' after parsing complete program",
                current_token, self.filename
            )

        return create_program(declarations)

    def synchronize(self):
        """Synchronize after a parse error."""
        # Prevent infinite loops by tracking position
        start_position = self.position
        max_tokens_to_skip = 100  # Safety limit
        tokens_skipped = 0

        while not self.at_end() and tokens_skipped < max_tokens_to_skip:
            if self.match(TokenType.TERMINATOR):
                self.advance()
                return

            # Look for keywords that start declarations
            if self.match(
                TokenType.FN,
                TokenType.STRUCT,
                TokenType.ENUM,
                TokenType.PUB,
                TokenType.IMPORT,
            ):
                return

            # Look for identifier followed by declaration operators (safer recovery)
            if self.match(TokenType.IDENTIFIER):
                next_token = self.peek()
                if next_token.type in (TokenType.DECLARE_CONST, TokenType.DECLARE_VAR):
                    return

            self.advance()
            tokens_skipped += 1

        # If we've skipped too many tokens, force advancement to EOF to prevent infinite loops
        if tokens_skipped >= max_tokens_to_skip and not self.at_end():
            self.position = len(self.tokens) - 1  # Move to EOF

    def parse_declaration(self) -> Optional[ASTNode]:
        """Parse top-level declarations."""
        # Skip any leading terminators at declaration level
        self.skip_terminators()

        # Check if we've reached the end after skipping terminators
        if self.at_end():
            return None

        start_token = self.current()

        # Handle public modifier
        is_public = False
        if self.match(TokenType.PUB):
            is_public = True
            self.advance()

        # Import declarations
        if self.match(TokenType.IMPORT):
            return self.parse_import()

        # Struct, enum, union declarations use Name :: keyword syntax
        # They are handled in parse_const_or_function_decl

        # Check for identifier followed by declaration operators
        if self.match(TokenType.IDENTIFIER):
            # Look ahead to see what kind of declaration this is
            if self.peek().type == TokenType.DECLARE_CONST:  # name ::
                return self.parse_const_or_function_decl(is_public)
            elif self.peek().type == TokenType.DECLARE_VAR:  # name :=
                return self.parse_var_decl(is_public)

        # Function declarations can also start with just 'fn'
        if self.match(TokenType.FN):
            return self.parse_function_decl_anonymous(is_public)

        # If we reach here, this is not a valid declaration
        raise ParseError.from_token(
            "Expected declaration (constant, variable, or function)",
            self.current(),
            self.filename,
        )

    def parse_import(self) -> ASTNode:
        """Parse import declarations."""
        import_token = self.consume(TokenType.IMPORT)

        # For now, simple import "module" format
        if self.match(TokenType.STRING_LITERAL):
            module_path = self.advance().value[1:-1]  # Remove quotes
            return ASTNode(
                kind=NodeKind.IMPORT,
                module_path=module_path,
                span=create_span_from_token(import_token),
            )

        raise ParseError.from_token(
            "Expected module path after import", self.current(), self.filename
        )

    def parse_const_or_function_decl(self, is_public: bool) -> ASTNode:
        """Parse constant, function, struct, enum, or union declaration (name :: ...)."""
        name_token = self.consume(TokenType.IDENTIFIER)
        name = name_token.value
        self.consume(TokenType.DECLARE_CONST)  # ::

        # Check if this is a function (fn keyword)
        if self.match(TokenType.FN):
            return self.parse_function_decl_with_name(name, is_public, name_token)

        # Check if this is a struct declaration
        if self.match(TokenType.STRUCT):
            return self.parse_struct_decl_with_name(name, is_public, name_token)

        # Check if this is an enum declaration
        if self.match(TokenType.ENUM):
            return self.parse_enum_decl_with_name(name, is_public, name_token)

        # Check if this is a union declaration
        if self.match(TokenType.UNION):
            return self.parse_union_decl_with_name(name, is_public, name_token)

        # Check if this is an import declaration
        if self.match(TokenType.IMPORT):
            self.advance()  # consume 'import'
            if self.match(TokenType.STRING_LITERAL):
                module_path = self.advance().value[1:-1]  # Remove quotes
                return ASTNode(
                    kind=NodeKind.IMPORT,
                    name=name,
                    module_path=module_path,
                    is_public=is_public,
                    span=create_span_from_token(name_token),
                )
            else:
                raise ParseError.from_token(
                    "Expected module path after import", self.current(), self.filename
                )

        # Otherwise it's a constant declaration
        value = self.parse_expression()
        return create_const_decl(
            name=name,
            value=value,
            is_public=is_public,
            span=create_span_from_token(name_token),
        )

    def parse_var_decl(self, is_public: bool) -> ASTNode:
        """Parse variable declaration (name := value)."""
        name_token = self.consume(TokenType.IDENTIFIER)
        name = name_token.value
        self.consume(TokenType.DECLARE_VAR)  # :=

        value = self.parse_expression()
        return create_var_decl(
            name=name,
            value=value,
            is_public=is_public,
            span=create_span_from_token(name_token),
        )

    def parse_function_decl_with_name(
        self, name: str, is_public: bool, name_token: Token
    ) -> ASTNode:
        """Parse function declaration after we have the name and :: fn."""
        self.consume(TokenType.FN)

        # Function parameters (which may include generics)
        self.consume(TokenType.LEFT_PAREN)
        generic_params, parameters = self.parse_mixed_parameters()

        # Return type (optional)
        return_type = None
        # Only parse return type if we don't immediately see a left brace
        # This handles functions like: fn() { ... } vs fn() i32 { ... }
        if not self.match(TokenType.LEFT_BRACE):
            # Check if this looks like a type (primitive types, identifiers, etc.)
            if self.match(
                TokenType.I8,
                TokenType.I16,
                TokenType.I32,
                TokenType.I64,
                TokenType.U8,
                TokenType.U16,
                TokenType.U32,
                TokenType.U64,
                TokenType.ISIZE,
                TokenType.USIZE,
                TokenType.F32,
                TokenType.F64,
                TokenType.BOOL,
                TokenType.CHAR,
                TokenType.STRING,
                TokenType.IDENTIFIER,
                TokenType.GENERIC_TYPE,
                TokenType.REF,
                TokenType.LEFT_BRACKET,
            ) or (self.match(TokenType.FN)):  # Function type
                return_type = self.parse_type()

        # Function body (required)
        if not self.match(TokenType.LEFT_BRACE):
            raise ParseError.from_token(
                "Expected function body after function signature",
                self.current(),
                self.filename,
            )
        body = self.parse_block()

        return create_function_decl(
            name=name,
            parameters=parameters,
            return_type=return_type,
            body=body,
            is_public=is_public,
            span=create_span_from_token(name_token),
        )

    def parse_function_decl_anonymous(self, is_public: bool) -> ASTNode:
        """Parse anonymous function declaration (fn (...) ...)."""
        fn_token = self.consume(TokenType.FN)

        # This is an error - anonymous functions should have names in declarations
        raise ParseError.from_token(
            "Function declarations must have names", fn_token, self.filename
        )

    def parse_generic_parameters(self) -> List[ASTNode]:
        """Parse generic type parameters ($T, $U, etc.)."""
        # For now, simple implementation
        params = []
        self.consume(TokenType.LEFT_PAREN)

        while not self.match(TokenType.RIGHT_PAREN) and not self.at_end():
            if self.match(TokenType.GENERIC_TYPE):
                generic_token = self.advance()
                # Extract the name without the $ prefix for consistency
                param_name = generic_token.value[1:]  # Remove '$' prefix
                param = ASTNode(kind=NodeKind.GENERIC_PARAM, name=param_name)
                params.append(param)

            if self.match(TokenType.COMMA):
                self.advance()
            else:
                break

        self.consume(TokenType.RIGHT_PAREN)
        return params

    def parse_mixed_parameters(self) -> tuple[List[ASTNode], List[ASTNode]]:
        """Parse mixed generic and function parameters from the same parentheses.
        Returns (generic_params, regular_params)."""
        generic_params = []
        regular_params = []

        while not self.match(TokenType.RIGHT_PAREN) and not self.at_end():
            self.skip_terminators()
            if self.match(TokenType.RIGHT_PAREN):
                break
            if self.match(TokenType.GENERIC_TYPE):
                # Parse generic parameter
                generic_token = self.advance()  # consume GENERIC_TYPE (e.g., $T)
                # Extract the name without the $ prefix for consistency
                param_name = generic_token.value[1:]  # Remove '$' prefix
                param = ASTNode(kind=NodeKind.GENERIC_PARAM, name=param_name)
                generic_params.append(param)
            else:
                # Parse regular function parameter
                param = self.parse_parameter()
                regular_params.append(param)

            # Handle comma
            if self.match(TokenType.COMMA):
                self.advance()
            elif not self.match(TokenType.RIGHT_PAREN):
                break

        self.skip_terminators()
        self.consume(TokenType.RIGHT_PAREN)
        return generic_params, regular_params

    def parse_parameter(self) -> ASTNode:
        """Parse function parameter."""
        name_token = self.consume(TokenType.IDENTIFIER)
        name = name_token.value
        self.consume(TokenType.COLON)
        param_type = self.parse_type()

        return create_parameter(
            name=name, param_type=param_type, span=create_span_from_token(name_token)
        )

    def parse_type(self) -> ASTNode:
        """Parse type expressions."""
        start_token = self.current()

        # Reference types: ref T
        if self.match(TokenType.REF):
            self.advance()
            target_type = self.parse_type()
            return ASTNode(
                kind=NodeKind.TYPE_POINTER,
                target_type=target_type,
                span=create_span_from_token(start_token),
            )

        # Array/slice types: [N]T or []T
        if self.match(TokenType.LEFT_BRACKET):
            self.advance()
            size = None

            # Check if it's a slice (empty brackets) or array (with size)
            if not self.match(TokenType.RIGHT_BRACKET):
                size = self.parse_expression()

            self.consume(TokenType.RIGHT_BRACKET)
            element_type = self.parse_type()

            if size:
                return ASTNode(
                    kind=NodeKind.TYPE_ARRAY,
                    element_type=element_type,
                    size=size,
                    span=create_span_from_token(start_token),
                )
            else:
                return ASTNode(
                    kind=NodeKind.TYPE_SLICE,
                    element_type=element_type,
                    span=create_span_from_token(start_token),
                )

        # Function types: fn(params) return_type
        if self.match(TokenType.FN):
            self.advance()
            # TODO: Implement function type parsing
            pass

        # Generic types: $T, $TYPE, etc.
        if self.match(TokenType.GENERIC_TYPE):
            generic_token = self.advance()
            # Remove the $ prefix for consistency
            type_name = generic_token.value[1:]
            return ASTNode(
                kind=NodeKind.TYPE_GENERIC,
                name=type_name,
                span=create_span_from_token(generic_token),
            )

        # Primitive or identifier types
        if self.match(TokenType.IDENTIFIER):
            type_name = self.advance().value
            return ASTNode(
                kind=NodeKind.TYPE_IDENTIFIER,
                name=type_name,
                span=create_span_from_token(start_token),
            )

        # Primitive types
        primitive_types = {
            TokenType.I8: "i8",
            TokenType.I16: "i16",
            TokenType.I32: "i32",
            TokenType.I64: "i64",
            TokenType.U8: "u8",
            TokenType.U16: "u16",
            TokenType.U32: "u32",
            TokenType.U64: "u64",
            TokenType.ISIZE: "isize",
            TokenType.USIZE: "usize",
            TokenType.F32: "f32",
            TokenType.F64: "f64",  # Note: These might need to be added to tokens
            TokenType.BOOL: "bool",
            TokenType.CHAR: "char",
            TokenType.STRING: "string",
        }

        for token_type, type_name in primitive_types.items():
            if self.match(token_type):
                self.advance()
                return create_primitive_type(
                    type_name, create_span_from_token(start_token)
                )

        raise ParseError.from_token("Expected type", self.current(), self.filename)

    def parse_block(self) -> ASTNode:
        """Parse block statement."""
        start_token = self.consume(TokenType.LEFT_BRACE)
        statements = []

        self.skip_terminators()

        while not self.match(TokenType.RIGHT_BRACE) and not self.at_end():
            try:
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
                self.skip_terminators()
            except ParseError as e:
                # Re-raise syntax errors inside function bodies
                # rather than attempting error recovery
                raise e

        end_token = self.consume(TokenType.RIGHT_BRACE)

        return create_block(
            statements=statements, span=create_span_from_tokens(start_token, end_token)
        )

    def parse_statement(self) -> Optional[ASTNode]:
        """Parse statements."""
        start_token = self.current()

        # Return statement
        if self.match(TokenType.RET):
            self.advance()
            value = None
            if not self.match(TokenType.TERMINATOR, TokenType.RIGHT_BRACE):
                value = self.parse_expression()
            return create_return_stmt(value, create_span_from_token(start_token))

        # Break statement
        if self.match(TokenType.BREAK):
            self.advance()
            return ASTNode(
                kind=NodeKind.BREAK, span=create_span_from_token(start_token)
            )

        # Continue statement
        if self.match(TokenType.CONTINUE):
            self.advance()
            return ASTNode(
                kind=NodeKind.CONTINUE, span=create_span_from_token(start_token)
            )

        # Fall statement (fallthrough in match)
        if self.match(TokenType.FALL):
            self.advance()
            return ASTNode(
                kind=NodeKind.FALL, span=create_span_from_token(start_token)
            )

        # Match statement
        if self.match(TokenType.MATCH):
            return self.parse_match_statement()

        # Defer statement
        if self.match(TokenType.DEFER):
            return self.parse_defer_statement()

        # If statement
        if self.match(TokenType.IF):
            return self.parse_if_statement()

        # While statement
        if self.match(TokenType.WHILE):
            return self.parse_while_statement()

        # For statement
        if self.match(TokenType.FOR):
            return self.parse_for_statement()

        # Block statement
        if self.match(TokenType.LEFT_BRACE):
            return self.parse_block()

        # Variable or constant declarations inside function body
        if self.match(TokenType.IDENTIFIER):
            lookahead = self.peek()
            if lookahead.type == TokenType.DECLARE_VAR:
                # Simple: name := value
                name_token = self.advance()
                self.consume(TokenType.DECLARE_VAR)
                value = self.parse_expression()
                return create_var_decl(
                    name=name_token.value,
                    value=value,
                    is_public=False,
                    span=create_span_from_token(name_token),
                )
            elif lookahead.type == TokenType.COLON:
                # Explicit type annotation: name: type = value
                name_token = self.advance()
                self.consume(TokenType.COLON)
                explicit_type = self.parse_type()
                self.consume(TokenType.ASSIGN)  # Use = for explicit type declarations
                value = self.parse_expression()
                var_decl = create_var_decl(
                    name=name_token.value,
                    value=value,
                    is_public=False,
                    span=create_span_from_token(name_token),
                )
                var_decl.explicit_type = explicit_type
                return var_decl
            elif lookahead.type == TokenType.DECLARE_CONST:
                # Constant or local type declaration: name :: value|struct|enum|union
                name_token = self.advance()
                self.consume(TokenType.DECLARE_CONST)
                
                # Check for struct/enum/union declarations
                if self.match(TokenType.STRUCT):
                    return self.parse_struct_decl_with_name(name_token.value, False, name_token)
                elif self.match(TokenType.ENUM):
                    return self.parse_enum_decl_with_name(name_token.value, False, name_token)
                elif self.match(TokenType.UNION):
                    return self.parse_union_decl_with_name(name_token.value, False, name_token)
                else:
                    # Regular constant declaration
                    value = self.parse_expression()
                    return create_const_decl(
                        name=name_token.value,
                        value=value,
                        is_public=False,
                        span=create_span_from_token(name_token),
                    )

        # Expression statement or assignment
        return self.parse_expression_or_assignment()

    def parse_if_statement(self) -> ASTNode:
        """Parse if statement."""
        if_token = self.consume(TokenType.IF)
        condition = self.parse_expression()
        then_stmt = self.parse_statement()

        else_stmt = None
        if self.match(TokenType.ELSE):
            self.advance()
            else_stmt = self.parse_statement()

        return ASTNode(
            kind=NodeKind.IF_STMT,
            condition=condition,
            then_stmt=then_stmt,
            else_stmt=else_stmt,
            span=create_span_from_token(if_token),
        )

    def parse_while_statement(self) -> ASTNode:
        """Parse while statement."""
        while_token = self.consume(TokenType.WHILE)
        condition = self.parse_expression()
        body = self.parse_statement()

        return ASTNode(
            kind=NodeKind.WHILE,
            condition=condition,
            body=body,
            span=create_span_from_token(while_token),
        )

    def parse_for_statement(self) -> ASTNode:
        """Parse for statement."""
        for_token = self.consume(TokenType.FOR)

        # Simple infinite loop: for { ... }
        if self.match(TokenType.LEFT_BRACE):
            body = self.parse_block()
            return ASTNode(
                kind=NodeKind.FOR, body=body, span=create_span_from_token(for_token)
            )

        # Check for range-based for loops: for var in iterable or for i, var in iterable
        if self.match(TokenType.IDENTIFIER):
            # Look ahead for the pattern
            first_identifier = self.current()
            self.advance()
            
            # Check for comma (indexed iteration): for i, value in arr
            if self.match(TokenType.COMMA):
                self.advance()  # consume comma
                if not self.match(TokenType.IDENTIFIER):
                    raise ParseError.from_token(
                        "Expected identifier after comma in for loop", 
                        self.current(), self.filename
                    )
                second_identifier = self.advance()
                
                if not self.match(TokenType.IN):
                    raise ParseError.from_token(
                        "Expected 'in' keyword in for loop", 
                        self.current(), self.filename
                    )
                self.consume(TokenType.IN)
                
                iterable = self.parse_expression()
                body = self.parse_block()
                
                return ASTNode(
                    kind=NodeKind.FOR_IN_INDEXED,
                    index_var=first_identifier.value,
                    iterator=second_identifier.value,
                    iterable=iterable,
                    body=body,
                    span=create_span_from_token(for_token),
                )
            
            # Check for 'in' (simple range-based): for value in arr
            elif self.match(TokenType.IN):
                self.consume(TokenType.IN)
                iterable = self.parse_expression()
                body = self.parse_block()
                
                return ASTNode(
                    kind=NodeKind.FOR_IN,
                    iterator=first_identifier.value,
                    iterable=iterable,
                    body=body,
                    span=create_span_from_token(for_token),
                )
            
            # Check for variable declaration: for i := 0; ... (C-style)
            elif self.match(TokenType.DECLARE_VAR):
                # Backtrack - we need to reparse this as a C-style for loop
                self.position -= 1  # Go back to the identifier
                
                # Parse init statement
                name_token = self.advance()
                self.consume(TokenType.DECLARE_VAR)
                value = self.parse_expression()
                init = create_var_decl(
                    name=name_token.value,
                    value=value,
                    is_public=False,
                    span=create_span_from_token(name_token),
                )
                
                if not self.match(TokenType.TERMINATOR):
                    raise ParseError.from_token(
                        "Expected ';' or newline in for loop", self.current(), self.filename
                    )
                self.consume(TokenType.TERMINATOR)

                # Parse condition
                condition = self.parse_expression()
                if not self.match(TokenType.TERMINATOR):
                    raise ParseError.from_token(
                        "Expected ';' or newline in for loop", self.current(), self.filename
                    )
                self.consume(TokenType.TERMINATOR)

                # Parse update
                update = self.parse_expression_or_assignment()

                # Parse body
                body = self.parse_block()

                return ASTNode(
                    kind=NodeKind.FOR,
                    init=init,
                    condition=condition,
                    update=update,
                    body=body,
                    span=create_span_from_token(for_token),
                )
            
            else:
                # Regular expression or assignment - this is also C-style
                # Backtrack and parse as expression
                self.position -= 1
                init = self.parse_expression_or_assignment()
                
                if not self.match(TokenType.TERMINATOR):
                    raise ParseError.from_token(
                        "Expected ';' or newline in for loop", self.current(), self.filename
                    )
                self.consume(TokenType.TERMINATOR)

                # Parse condition
                condition = self.parse_expression()
                if not self.match(TokenType.TERMINATOR):
                    raise ParseError.from_token(
                        "Expected ';' or newline in for loop", self.current(), self.filename
                    )
                self.consume(TokenType.TERMINATOR)

                # Parse update
                update = self.parse_expression_or_assignment()

                # Parse body
                body = self.parse_block()

                return ASTNode(
                    kind=NodeKind.FOR,
                    init=init,
                    condition=condition,
                    update=update,
                    body=body,
                    span=create_span_from_token(for_token),
                )

        # If we don't start with an identifier, this might be a malformed for loop
        raise ParseError.from_token(
            "Expected identifier or '{' after 'for' keyword", 
            self.current(), self.filename
        )

    def parse_expression_or_assignment(self) -> ASTNode:
        """Parse expression statement or assignment."""
        expr = self.parse_expression()

        # Check for assignment operators
        if self.match(
            TokenType.ASSIGN,
            TokenType.PLUS_ASSIGN,
            TokenType.MINUS_ASSIGN,
            TokenType.MULTIPLY_ASSIGN,
            TokenType.DIVIDE_ASSIGN,
            TokenType.MODULO_ASSIGN,
            TokenType.BITWISE_AND_ASSIGN,
            TokenType.BITWISE_OR_ASSIGN,
            TokenType.BITWISE_XOR_ASSIGN,
            TokenType.LEFT_SHIFT_ASSIGN,
            TokenType.RIGHT_SHIFT_ASSIGN,
        ):
            op_token = self.advance()
            assign_op = token_to_assign_op(op_token.type)
            if assign_op:
                value = self.parse_expression()
                return create_assignment_stmt(
                    target=expr, op=assign_op, value=value, span=expr.span
                )

        # Validate that this expression is valid as a statement
        if not self._is_valid_expression_statement(expr):
            # Provide more specific error messages for common cases
            if expr.kind == NodeKind.IDENTIFIER:
                # Check if this looks like a missing assignment operator
                if self.match(
                    TokenType.INTEGER_LITERAL,
                    TokenType.FLOAT_LITERAL,
                    TokenType.STRING_LITERAL,
                    TokenType.CHAR_LITERAL,
                ):
                    raise ParseError.from_token(
                        f"Missing assignment operator (:= or =) between identifier and value",
                        self.current(),
                        self.filename,
                    )
                else:
                    raise ParseError.from_token(
                        f"Identifier '{expr.name if hasattr(expr, 'name') else 'unknown'}' cannot be used as a statement",
                        self.current(),
                        self.filename,
                    )
            else:
                raise ParseError.from_token(
                    f"Expression of type {expr.kind.name} cannot be used as a statement",
                    self.current(),
                    self.filename,
                )

        # Otherwise it's an expression statement
        return ASTNode(
            kind=NodeKind.EXPRESSION_STMT,
            expression=expr,
            span=expr.span if expr else None,
        )

    def _is_valid_expression_statement(self, expr: ASTNode) -> bool:
        """Check if an expression is valid as a standalone statement."""
        # These expression types are NOT valid as standalone statements
        invalid_as_statements = {
            NodeKind.LITERAL,  # Standalone literals like 42, "hello"
            NodeKind.IDENTIFIER,  # Standalone identifiers like x
        }

        # All other expressions (calls, binary ops, unary ops, etc.) are valid
        return expr.kind not in invalid_as_statements

    def parse_expression(self) -> ASTNode:
        """Parse expressions using precedence climbing."""
        return self.parse_binary_expression(0)

    def parse_binary_expression(self, min_precedence: int) -> ASTNode:
        """Parse binary expressions with precedence climbing."""
        left = self.parse_unary_expression()

        while True:
            # Check if current token is a binary operator
            if not self.match(
                TokenType.PLUS,
                TokenType.MINUS,
                TokenType.MULTIPLY,
                TokenType.DIVIDE,
                TokenType.MODULO,
                TokenType.EQUAL,
                TokenType.NOT_EQUAL,
                TokenType.LESS_THAN,
                TokenType.LESS_EQUAL,
                TokenType.GREATER_THAN,
                TokenType.GREATER_EQUAL,
                TokenType.AND,
                TokenType.OR,
                TokenType.BITWISE_AND,
                TokenType.BITWISE_OR,
                TokenType.BITWISE_XOR,
                TokenType.LEFT_SHIFT,
                TokenType.RIGHT_SHIFT,
            ):
                break

            op_token = self.current()
            binary_op = token_to_binary_op(op_token.type)
            if not binary_op:
                break

            precedence = get_binary_precedence(binary_op)
            if precedence < min_precedence:
                break

            self.advance()  # Consume operator

            # Check if we're at end of input or terminator after operator
            if self.at_end() or self.match(TokenType.TERMINATOR, TokenType.RIGHT_PAREN, 
                                           TokenType.RIGHT_BRACE, TokenType.RIGHT_BRACKET,
                                           TokenType.COMMA):
                raise ParseError.from_token(
                    f"Expected expression after '{op_token.value}' operator",
                    self.current(), self.filename
                )

            # Right associative operators would use precedence here,
            # but A7 operators are left associative
            right = self.parse_binary_expression(precedence + 1)

            # Validate that we got a valid right operand
            if not right:
                raise ParseError.from_token(
                    f"Expected expression after '{op_token.value}' operator",
                    self.current(), self.filename
                )

            left = create_binary_expr(left, binary_op, right)

        return left

    def parse_unary_expression(self) -> ASTNode:
        """Parse unary expressions."""
        start_token = self.current()

        # Unary operators
        if self.match(
            TokenType.MINUS,
            TokenType.NOT,
            TokenType.LOGICAL_NOT,
            TokenType.BITWISE_NOT,
        ):
            op_token = self.advance()
            unary_op = token_to_unary_op(op_token.type)
            if unary_op:
                operand = self.parse_unary_expression()
                return ASTNode(
                    kind=NodeKind.UNARY,
                    operator=unary_op,
                    operand=operand,
                    span=create_span_from_token(start_token),
                )

        return self.parse_postfix_expression()

    def parse_postfix_expression(self) -> ASTNode:
        """Parse postfix expressions (calls, indexing, field access)."""
        expr = self.parse_primary_expression()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                # Function call
                expr = self.parse_call_expression(expr)
            elif self.match(TokenType.LEFT_BRACKET):
                # Array indexing
                expr = self.parse_index_expression(expr)
            elif self.match(TokenType.DOT):
                # Field access or dereference
                expr = self.parse_field_or_deref_expression(expr)
            else:
                break

        return expr

    def parse_call_expression(self, function: ASTNode) -> ASTNode:
        """Parse function call expression."""
        self.consume(TokenType.LEFT_PAREN)
        arguments = []

        if not self.match(TokenType.RIGHT_PAREN):
            arguments.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                self.advance()
                arguments.append(self.parse_expression())

        self.consume(TokenType.RIGHT_PAREN)

        return create_call_expr(
            function=function, arguments=arguments, span=function.span
        )

    def parse_index_expression(self, object_expr: ASTNode) -> ASTNode:
        """Parse array indexing expression."""
        self.consume(TokenType.LEFT_BRACKET)

        # Check for slice notation
        if self.match(TokenType.DOT_DOT):
            # This is a slice [..end]
            self.advance()
            end = (
                self.parse_expression()
                if not self.match(TokenType.RIGHT_BRACKET)
                else None
            )
            self.consume(TokenType.RIGHT_BRACKET)

            return ASTNode(
                kind=NodeKind.SLICE,
                object=object_expr,
                start=None,
                end=end,
                span=object_expr.span,
            )

        index = self.parse_expression()

        # Check for slice notation
        if self.match(TokenType.DOT_DOT):
            self.advance()
            end = (
                self.parse_expression()
                if not self.match(TokenType.RIGHT_BRACKET)
                else None
            )
            self.consume(TokenType.RIGHT_BRACKET)

            return ASTNode(
                kind=NodeKind.SLICE,
                object=object_expr,
                start=index,
                end=end,
                span=object_expr.span,
            )

        self.consume(TokenType.RIGHT_BRACKET)

        return ASTNode(
            kind=NodeKind.INDEX, object=object_expr, index=index, span=object_expr.span
        )

    def parse_field_or_deref_expression(self, object_expr: ASTNode) -> ASTNode:
        """Parse field access, address-of (.adr), or pointer dereference (.val)."""
        self.consume(TokenType.DOT)

        # Field access (including special .adr and .val)
        if self.match(TokenType.IDENTIFIER):
            field_name = self.advance().value
            
            # Check for special address-of operation
            if field_name == "adr":
                return ASTNode(
                    kind=NodeKind.ADDRESS_OF, 
                    operand=object_expr, 
                    span=object_expr.span
                )
            
            # Check for special dereference operation
            elif field_name == "val":
                return ASTNode(
                    kind=NodeKind.DEREF, 
                    pointer=object_expr, 
                    span=object_expr.span
                )
            
            # Regular field access
            else:
                return ASTNode(
                    kind=NodeKind.FIELD_ACCESS,
                    object=object_expr,
                    field=field_name,
                    span=object_expr.span,
                )

        raise ParseError.from_token(
            "Expected field name after '.'", self.current(), self.filename
        )

    def parse_primary_expression(self) -> ASTNode:
        """Parse primary expressions."""
        start_token = self.current()

        # Literals
        if self.match(
            TokenType.INTEGER_LITERAL,
            TokenType.FLOAT_LITERAL,
            TokenType.CHAR_LITERAL,
            TokenType.STRING_LITERAL,
            TokenType.TRUE_LITERAL,
            TokenType.FALSE_LITERAL,
            TokenType.NIL_LITERAL,
        ):
            return create_literal_from_token(self.advance())

        # Array literals: [1, 2, 3]
        if self.match(TokenType.LEFT_BRACKET):
            return self.parse_array_literal()

        # Identifiers, cast expressions, or struct literals
        if self.match(TokenType.IDENTIFIER):
            name = self.advance().value
            
            # Check for cast expression: cast(type, expr)
            if name == "cast" and self.match(TokenType.LEFT_PAREN):
                return self.parse_cast_expression(start_token)
            
            # Check for struct literal: Person{...}
            # Only parse as struct literal if we're in an appropriate context
            # (not in a statement context where { would start a block)
            if self.match(TokenType.LEFT_BRACE) and self._should_parse_struct_literal():
                return self.parse_struct_literal(
                    name, create_span_from_token(start_token)
                )
            else:
                return create_identifier(name, create_span_from_token(start_token))

        # Parenthesized expressions
        if self.match(TokenType.LEFT_PAREN):
            self.advance()
            expr = self.parse_expression()
            self.consume(TokenType.RIGHT_PAREN)
            return expr

        # If expressions
        if self.match(TokenType.IF):
            return self.parse_if_expression()

        raise ParseError.from_token(
            "Expected expression", self.current(), self.filename
        )

    def parse_cast_expression(self, start_token: Token) -> ASTNode:
        """Parse cast expression: cast(type, expr)"""
        self.advance()  # consume '('
        
        # Parse the target type
        target_type = self.parse_type()
        
        # Expect comma
        self.consume(TokenType.COMMA, "Expected ',' after type in cast expression")
        
        # Parse the expression to cast
        expression = self.parse_expression()
        
        # Expect closing paren
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after cast expression")
        
        return create_cast_expr(
            target_type=target_type,
            expression=expression,
            span=create_span_from_token(start_token)
        )
    
    def parse_if_expression(self) -> ASTNode:
        """Parse if expressions."""
        if_token = self.consume(TokenType.IF)
        condition = self.parse_expression()
        self.consume(TokenType.LEFT_BRACE)
        then_expr = self.parse_expression()
        self.consume(TokenType.RIGHT_BRACE)

        else_expr = None
        if self.match(TokenType.ELSE):
            self.advance()
            self.consume(TokenType.LEFT_BRACE)
            else_expr = self.parse_expression()
            self.consume(TokenType.RIGHT_BRACE)

        return ASTNode(
            kind=NodeKind.IF_EXPR,
            condition=condition,
            then_expr=then_expr,
            else_expr=else_expr,
            span=create_span_from_token(if_token),
        )

    def parse_array_literal(self) -> ASTNode:
        """Parse array literals: [1, 2, 3]"""
        start_token = self.consume(TokenType.LEFT_BRACKET)
        elements = []

        if not self.match(TokenType.RIGHT_BRACKET):
            elements.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                self.advance()
                if self.match(TokenType.RIGHT_BRACKET):  # Handle trailing comma
                    break
                elements.append(self.parse_expression())

        self.consume(TokenType.RIGHT_BRACKET)

        return ASTNode(
            kind=NodeKind.ARRAY_INIT,
            elements=elements,
            span=create_span_from_token(start_token),
        )

    def parse_struct_literal(self, struct_name: str, span: SourceSpan) -> ASTNode:
        """Parse struct literals: Person{name: "John", age: 30} or Token{1, [10, 20, 30]}"""
        self.consume(TokenType.LEFT_BRACE)
        field_inits = []

        # Skip terminators after opening brace
        self.skip_terminators()

        if not self.match(TokenType.RIGHT_BRACE):
            # Check if this is named field initialization or positional initialization
            # Look ahead to see if we have identifier followed by colon
            is_named = (self.match(TokenType.IDENTIFIER) and self.peek().type == TokenType.COLON)
            
            if is_named:
                # Named field initialization: field_name: value
                field_name_token = self.consume(TokenType.IDENTIFIER)
                self.consume(TokenType.COLON)
                field_value = self.parse_expression()

                field_init = ASTNode(
                    kind=NodeKind.FIELD_INIT,
                    name=field_name_token.value,
                    value=field_value,
                    span=create_span_from_token(field_name_token),
                )
                field_inits.append(field_init)

                while self.match(TokenType.COMMA):
                    self.advance()
                    self.skip_terminators()  # Skip terminators after comma
                    if self.match(TokenType.RIGHT_BRACE):  # Handle trailing comma
                        break
                    field_name_token = self.consume(TokenType.IDENTIFIER)
                    self.consume(TokenType.COLON)
                    field_value = self.parse_expression()

                    field_init = ASTNode(
                        kind=NodeKind.FIELD_INIT,
                        name=field_name_token.value,
                        value=field_value,
                        span=create_span_from_token(field_name_token),
                    )
                    field_inits.append(field_init)
            else:
                # Positional initialization: value1, value2, ...
                field_value = self.parse_expression()
                field_init = ASTNode(
                    kind=NodeKind.FIELD_INIT,
                    name=None,  # No name for positional init
                    value=field_value,
                    span=field_value.span,
                )
                field_inits.append(field_init)

                while self.match(TokenType.COMMA):
                    self.advance()
                    if self.match(TokenType.RIGHT_BRACE):  # Handle trailing comma
                        break
                    field_value = self.parse_expression()
                    field_init = ASTNode(
                        kind=NodeKind.FIELD_INIT,
                        name=None,  # No name for positional init
                        value=field_value,
                        span=field_value.span,
                    )
                    field_inits.append(field_init)

        # Skip terminators before closing brace
        self.skip_terminators()
        self.consume(TokenType.RIGHT_BRACE)

        return ASTNode(
            kind=NodeKind.STRUCT_INIT,
            struct_type=struct_name,
            field_inits=field_inits,
            span=span,
        )

    def parse_struct_decl_with_name(
        self, name: str, is_public: bool, name_token: Token
    ) -> ASTNode:
        """Parse struct declarations when name is already parsed."""
        struct_token = self.consume(TokenType.STRUCT)

        # Generic parameters (optional)
        generic_params = []
        if (
            self.match(TokenType.LEFT_PAREN)
            and self.peek().type == TokenType.GENERIC_TYPE
        ):
            generic_params = self.parse_generic_parameters()

        # Struct body
        self.consume(TokenType.LEFT_BRACE)
        fields = []

        while not self.match(TokenType.RIGHT_BRACE) and not self.at_end():
            self.skip_terminators()
            if self.match(TokenType.RIGHT_BRACE):
                break
            field_name_token = self.consume(TokenType.IDENTIFIER)
            self.consume(TokenType.COLON)
            field_type = self.parse_type()

            field = ASTNode(
                kind=NodeKind.FIELD,
                name=field_name_token.value,
                field_type=field_type,
                span=create_span_from_token(field_name_token),
            )
            fields.append(field)

            # Skip comma if present
            if self.match(TokenType.COMMA):
                self.advance()

            self.skip_terminators()

        self.consume(TokenType.RIGHT_BRACE)

        return ASTNode(
            kind=NodeKind.STRUCT,
            name=name,
            fields=fields,
            generic_params=generic_params,
            is_public=is_public,
            span=create_span_from_token(name_token),
        )

    def parse_enum_decl_with_name(
        self, name: str, is_public: bool, name_token: Token
    ) -> ASTNode:
        """Parse enum declarations when name is already parsed."""
        enum_token = self.consume(TokenType.ENUM)

        # Enum body
        self.consume(TokenType.LEFT_BRACE)
        variants = []

        self.skip_terminators()

        while not self.match(TokenType.RIGHT_BRACE) and not self.at_end():
            variant_name_token = self.consume(TokenType.IDENTIFIER)
            variant_value = None

            # Optional explicit value
            if self.match(TokenType.ASSIGN):
                self.advance()
                variant_value = self.parse_expression()

            variant = ASTNode(
                kind=NodeKind.ENUM_VARIANT,
                name=variant_name_token.value,
                value=variant_value,
                span=create_span_from_token(variant_name_token),
            )
            variants.append(variant)

            # Skip comma if present
            if self.match(TokenType.COMMA):
                self.advance()

            self.skip_terminators()

        self.consume(TokenType.RIGHT_BRACE)

        return ASTNode(
            kind=NodeKind.ENUM,
            name=name,
            variants=variants,
            is_public=is_public,
            span=create_span_from_token(name_token),
        )

    def parse_union_decl_with_name(
        self, name: str, is_public: bool, name_token: Token
    ) -> ASTNode:
        """Parse union declarations when name is already parsed."""
        union_token = self.consume(TokenType.UNION)

        # Check for tagged union
        is_tagged = False
        if self.match(TokenType.LEFT_PAREN):
            self.advance()
            if self.match(TokenType.IDENTIFIER) and self.current().value == "tag":
                is_tagged = True
                self.advance()
            self.consume(TokenType.RIGHT_PAREN)

        # Union body
        self.consume(TokenType.LEFT_BRACE)
        fields = []

        while not self.match(TokenType.RIGHT_BRACE) and not self.at_end():
            field_name_token = self.consume(TokenType.IDENTIFIER)
            self.consume(TokenType.COLON)
            field_type = self.parse_type()

            field = ASTNode(
                kind=NodeKind.FIELD,
                name=field_name_token.value,
                field_type=field_type,
                span=create_span_from_token(field_name_token),
            )
            fields.append(field)

            # Skip comma if present
            if self.match(TokenType.COMMA):
                self.advance()

            self.skip_terminators()

        self.consume(TokenType.RIGHT_BRACE)

        return ASTNode(
            kind=NodeKind.UNION,
            name=name,
            fields=fields,
            is_tagged=is_tagged,
            is_public=is_public,
            span=create_span_from_token(name_token),
        )

    def parse_pattern(self) -> ASTNode:
        """Parse match patterns including ranges, literals, and enum access."""
        start_token = self.current()
        
        # Parse the first part of the pattern
        pattern = self.parse_primary_pattern()
        
        # Check for range pattern: expr..expr
        if self.match(TokenType.DOT_DOT):
            self.advance()  # consume '..'
            end_pattern = self.parse_primary_pattern()
            
            return ASTNode(
                kind=NodeKind.PATTERN_RANGE,
                start=pattern,
                end=end_pattern,
                span=create_span_from_token(start_token),
            )
        
        return pattern

    def parse_primary_pattern(self) -> ASTNode:
        """Parse primary pattern elements (literals, identifiers with dots)."""
        start_token = self.current()
        
        # Literals
        if self.match(
            TokenType.INTEGER_LITERAL,
            TokenType.FLOAT_LITERAL,
            TokenType.CHAR_LITERAL,
            TokenType.STRING_LITERAL,
        ):
            return ASTNode(
                kind=NodeKind.PATTERN_LITERAL,
                literal=create_literal_from_token(self.advance()),
                span=create_span_from_token(start_token),
            )
        
        # Identifiers and enum access patterns  
        if self.match(TokenType.IDENTIFIER):
            first_identifier = self.advance()
            
            # Check for enum access: EnumType.Variant
            if self.match(TokenType.DOT):
                self.advance()  # consume '.'
                if not self.match(TokenType.IDENTIFIER):
                    raise ParseError.from_token(
                        "Expected identifier after '.' in pattern", 
                        self.current(), self.filename
                    )
                variant_identifier = self.advance()
                
                return ASTNode(
                    kind=NodeKind.PATTERN_ENUM,
                    enum_type=first_identifier.value,
                    variant=variant_identifier.value,
                    span=create_span_from_token(start_token),
                )
            else:
                # Simple identifier pattern
                return ASTNode(
                    kind=NodeKind.PATTERN_IDENTIFIER,
                    name=first_identifier.value,
                    span=create_span_from_token(start_token),
                )
        
        # Fall back to expression parsing for complex patterns
        return self.parse_expression()

    def parse_match_statement(self) -> ASTNode:
        """Parse match statements."""
        match_token = self.consume(TokenType.MATCH)
        expression = self.parse_expression()

        self.consume(TokenType.LEFT_BRACE)
        cases = []
        else_case = None

        while not self.match(TokenType.RIGHT_BRACE) and not self.at_end():
            if self.match(TokenType.CASE):
                case_token = self.advance()

                # Parse patterns (supporting ranges, multiple values, enum access)
                patterns = [self.parse_pattern()]
                while self.match(TokenType.COMMA):
                    self.advance()
                    patterns.append(self.parse_pattern())

                self.consume(TokenType.COLON)
                body = self.parse_statement()

                case_node = ASTNode(
                    kind=NodeKind.CASE_BRANCH,
                    patterns=patterns,
                    statement=body,
                    span=create_span_from_token(case_token),
                )
                cases.append(case_node)

            elif self.match(TokenType.ELSE):
                else_token = self.advance()
                self.consume(TokenType.COLON)
                else_case = [self.parse_statement()]

            self.skip_terminators()

        self.consume(TokenType.RIGHT_BRACE)

        return ASTNode(
            kind=NodeKind.MATCH,
            expression=expression,
            cases=cases,
            else_case=else_case,
            span=create_span_from_token(match_token),
        )

    def parse_defer_statement(self) -> ASTNode:
        """Parse defer statements."""
        defer_token = self.consume(TokenType.DEFER)
        statement = self.parse_statement()

        return ASTNode(
            kind=NodeKind.DEFER,
            statement=statement,
            span=create_span_from_token(defer_token),
        )


def parse_a7(source_code: str, filename: Optional[str] = None) -> ASTNode:
    """Parse A7 source code and return an AST."""
    tokenizer = Tokenizer(source_code, filename)
    tokens = tokenizer.tokenize()
    source_lines = source_code.splitlines() if source_code else []
    parser = Parser(tokens, filename, source_lines)
    return parser.parse()
