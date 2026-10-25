# Parser class
from .lexer import Lexer, Token
from ..error import MiniError
from .ast import AtomicNode, BinaryNode, BlockNode, IfNode, LambdaNode, ListNode, MapNode, Node, ProgramNode, SliceNode, TupleNode, UnaryNode, WhileNode, ForNode, ControlNode

# Left associative infix operators binding powers
precedence_left = {
    'DOT': 160,
    'CALL': 150,
    'INDEX': 150,
    'POWER':    140,
    'MULTIPLY': 120,
    'DIVIDE':   120,
    'MODULO':   120,
    'PLUS':     110,
    'MINUS':    110,
    'BITWISEAND': 90,
    'BITWISEOR': 70,
    'RANGE': 65,
    'LESS':     60,
    'LESSEQUAL':60,
    'GREATER':  60,
    'GREATEREQUAL': 60,
    'NOTEQUAL': 60,
    'EQUAL':    60,
    'PLUSEQUAL': 20,
    'MINUSEQUAL': 50,
    'TIMESEQUAL': 50,
    'DIVEQUAL': 50,
    'MODEQUAL': 50,
    'POWEQUAL': 50,
    'AND':      40,
    'OR':       30,
    'ASSIGNMENT': 20,
}

# Parser class
class Parser:
    def __init__(self, lexer: Lexer, debug = False):
        self.lexer = lexer
        self.debug = debug
        self.loop_depth = 0
        self.function_depth = 0

    # Helper functions
    def __dprint(self, *args):
        """
        Print debug messages.
        """
        if self.debug:
            print(*args)

    def __error(self, msg: str, token: Token):
        """
        Raise an error with the given message.
        """
        raise MiniError("Syntax", msg, token)

    def __expect(self, token_name: str):
        """
        Expect a token from the lexer.
        """
        t = self.lexer.next_token()
        if t.name != token_name:
            self.__error(f"Expected {token_name} but got {t.name}", t)
        return t

    # Tokenizer functions
    def __parse_list_of_expressions(self, delimiter: str, end_delimiter: str, accept_trailing_delimiter: bool) -> list[Node]:
        """
        Parse a list of expressions from the lexer and return them as a list.
        The expressions are separated by the given delimiter and the list ends with the given end delimiter.
        No start delimiter is required.
        If accept_trailing_delimiter is True, a trailing delimiter before the end delimiter is accepted.
        """
        expressions = []
        nt = self.lexer.peek_token()
        while nt.name != end_delimiter:
            if nt.name == "EOF":
                self.__error(f"Expected {end_delimiter} before end of input", nt)
            expressions.append(self.__parse_expression())
            nt = self.lexer.peek_token()
            # Check for the delimiter after an expression
            if nt.name == delimiter:
                self.lexer.next_token()
                nt = self.lexer.peek_token()
                # If a trailing delimiter is accepted and the end delimiter is next, break the loop
                if accept_trailing_delimiter and nt.name == end_delimiter:
                    break
            elif nt.name != end_delimiter:
                self.__error(f"Expected '{delimiter}' or '{end_delimiter}' but got '{nt.name}'", nt)
        self.lexer.next_token() # Remove the end delimiter
        return expressions

    def __parse_expressions_until(self, end_delimiter: str) -> list[Node]:
        """
        Parse a list of expressions from the lexer and return them as a list.
        The expressions are ended with the given end delimiter.
        """
        expressions = []
        nt = self.lexer.peek_token()
        while nt.name != end_delimiter:
            if nt.name == "EOF":
                self.__error(f"Expected {end_delimiter} before end of input", nt)
            expressions.append(self.__parse_expression())
            nt = self.lexer.peek_token()
        self.lexer.next_token()
        return expressions

    def __ident_list_to_str(self, nodes: list[Node]) -> list[str]:
        """
        Convert and verify a list of identifiers and return a list of strings.
        """
        result = []
        for e in nodes:
            if not (isinstance(e, AtomicNode) and e.type == "identifier"):
                self.__error("Function parameter must be an identifier", e.location)
            if e.value in result:
                self.__error(f"Duplicate parameter '{e.value}'", e.location)
            result.append(e.value)
        return result

    def __parse_primary(self) -> Node:
        token = self.lexer.peek_token()
        node = self.__parse_primary_value()
        if node.location is None:
            node.at(token)
        return node

    def __parse_primary_value(self) -> Node:
        """
        Parse a primary expression from the lexer.
        """
        t = self.lexer.next_token()
        if t.name in ["IDENTIFIER", "STRING", "NUMBER", "BOOL"]:
            value = AtomicNode(t.name.lower(), t.value).at(t)
            nt = self.lexer.peek_token()
            if nt.name == "RIGHTARROW":
                return self.__parse_lambda([value])
            else:
                return value
        elif t.name == "KEYWORD":
            match t.value:
                case "if": return self.__parse_if()
                case "while":
                    condition = self.__parse_expression()
                    return WhileNode(condition, self.__parse_loop_body())
                case "for":
                    if self.lexer.peek_token().name != "IDENTIFIER":
                        self.__error("Expected IDENTIFIER for for binding; patterns are not supported in v1", self.lexer.peek_token())
                    variable = self.__expect("IDENTIFIER")
                    self.__expect("IN")
                    iterable = self.__parse_expression()
                    return ForNode(variable.value, iterable, self.__parse_loop_body())
                case "break" | "continue":
                    if not self.loop_depth:
                        self.__error(f"'{t.value}' is only valid inside a loop body in the same function", t)
                    return ControlNode(t.value)
                case "return":
                    if not self.function_depth:
                        self.__error("'return' is only valid inside a function", t)
                    if self.lexer.peek_token().name in ["EOF", "RBRACE"]:
                        self.__error("Return requires a value; use 'return ()' for unit", t)
                    return ControlNode("return", self.__parse_expression())
                case "none": self.__error("'none' is not supported in v1; use () for unit", t)
                case "else": self.__error("Unexpected 'else' without a matching if", t)
                case _: self.__error(f"Keyword '{t.value}' is not supported in v1", t)
        elif t.name == "LPAREN":
            lhs = TupleNode(self.__parse_list_of_expressions("COMMA", "RPAREN", False))
            # Check for trailing right arrow
            nt = self.lexer.peek_token()
            if nt.name == "RIGHTARROW":
                return self.__parse_lambda(lhs.elements)
            else:
                if len(lhs.elements) == 1:
                    lhs = lhs.elements[0]
                return lhs
        elif t.name == "LBRACKET":
            return ListNode(self.__parse_list_of_expressions("COMMA", "RBRACKET", True))
        elif t.name == "HASHBRACE":
            return self.__parse_hash_map()
        elif t.name == "LBRACE":
            return BlockNode(self.__parse_expressions_until("RBRACE"))
        elif t.name in ["MINUS", "NOT"]:
            return UnaryNode(t.name, self.__parse_binary_expression(self.__parse_primary(), precedence_left["CALL"]))
        else:
            if t.name == "COLON":
                self.__error("Colon bodies are not supported in v1; use braces", t)
            if t.name == "SEMICOLON":
                self.__error("Semicolons are not supported in v1; use whitespace", t)
            if t.name in ["BITWISEAND", "BITWISEOR", "BITWISENOT", "IS", "IN", "QUESTIONMARK"]:
                self.__error(f"Operator '{t.value}' is not supported in v1", t)
            self.__error(f"Expected primary expression but got '{t.name}'", t)

    def __parse_lambda(self, args: list[Node]) -> LambdaNode:
        """
        Parse a lambda expression from the lexer.
        """
        self.__expect("RIGHTARROW")
        # Validate that the tuple only has identifiers
        # And add them to a list of argument names
        params = self.__ident_list_to_str(args)
        # Parse the body of the lambda
        body = self.__parse_function_body()
        return LambdaNode(params, body)

    def __parse_loop_body(self) -> Node:
        self.loop_depth += 1
        try:
            return self.__parse_expression()
        finally:
            self.loop_depth -= 1

    def __parse_function_body(self) -> Node:
        # A function declared in a loop cannot break/continue its caller's loop.
        outer_loop_depth = self.loop_depth
        self.loop_depth = 0
        self.function_depth += 1
        try:
            return self.__parse_expression()
        finally:
            self.function_depth -= 1
            self.loop_depth = outer_loop_depth

    def __parse_binary_expression(self, lhs: Node, precedence: int) -> Node:
        """Precedence climbing, with right-associative assignment."""
        while True:
            token = self.lexer.peek_token()
            op = token.name
            if op in ["BITWISEAND", "BITWISEOR", "BITWISENOT", "IS", "IN",
                      "MINUSEQUAL", "TIMESEQUAL", "DIVEQUAL", "MODEQUAL", "POWEQUAL", "QUESTIONMARK"]:
                self.__error(f"Operator '{token.value}' is not supported in v1", token)
            if op not in precedence_left or precedence_left[op] < precedence:
                return lhs
            self.lexer.next_token()
            if op == "RANGE" and self.lexer.peek_token().name in ["EOF", "LBRACE", "RBRACE", "RPAREN", "RBRACKET", "COMMA"]:
                self.__error("Range requires both bounds; open-ended ranges are not supported in v1", token)
            if op == "INDEX":
                rhs = self.__parse_expression()
                if self.lexer.peek_token().name == "COLON":
                    self.lexer.next_token()
                    end = self.__parse_expression()
                    step = None
                    if self.lexer.peek_token().name == "COLON":
                        self.lexer.next_token()
                        step = self.__parse_expression()
                    rhs = SliceNode(rhs, end, step).at(token)
                self.__expect("RBRACKET")
            elif op == "CALL":
                rhs = TupleNode(self.__parse_list_of_expressions("COMMA", "RPAREN", False))
            elif op == "DOT":
                member = self.__expect("IDENTIFIER")
                rhs = AtomicNode("identifier", member.value).at(member)
            elif op == "ASSIGNMENT" and isinstance(lhs, BinaryNode) and lhs.operator == "CALL":
                if not isinstance(lhs.left, AtomicNode) or lhs.left.type != "identifier":
                    self.__error("Function name must be an identifier", token)
                self.__ident_list_to_str(lhs.right.elements)
                rhs = self.__parse_function_body()
            else:
                # Assignment chains bind right; arithmetic binds left.
                minimum = precedence_left[op] + (0 if op == "ASSIGNMENT" else 1)
                rhs = self.__parse_binary_expression(self.__parse_primary(), minimum)
            lhs = BinaryNode(op, lhs, rhs).at(token)

    def __parse_hash_map(self) -> MapNode:
        """
        Parse a hash map from the lexer.
        Example: { "key1" : "value1", key2 : "value2", 12 : "value3" }
        """
        pairs = {}
        nt = self.lexer.peek_token()
        while nt.name != "RBRACE":
            key = self.__parse_primary()
            self.__expect("COLON")
            value = self.__parse_expression()
            if key in pairs:
                self.__error(f"Duplicate key '{key}' in hash map", key.location)
            pairs[key] = value
            nt = self.lexer.peek_token()
            if nt.name == "COMMA":
                self.lexer.next_token()
            elif nt.name != "RBRACE":
                self.__error(f"Expected 'COMMA' or 'RBRACE' but got '{nt.name}'", nt)
        self.lexer.next_token() # Remove the end delimiter
        return MapNode(pairs)

    def __parse_if(self) -> IfNode:
        condition = self.__parse_expression()
        body = self.__parse_expression()
        otherwise = None
        token = self.lexer.peek_token()
        if token.name == "KEYWORD" and token.value == "else":
            self.lexer.next_token()
            otherwise = self.__parse_expression()
        return IfNode(condition, body, [], otherwise)

    def __parse_expression(self) -> Node:
        """
        Parse an expression from the lexer.
        """
        return self.__parse_binary_expression(self.__parse_primary(), 0)

    def parse(self):
        """
        Parse the source into an abstract syntax tree.
        """
        program = ProgramNode([])
        while not self.lexer.is_done():
            e = self.__parse_expression()
            program.expressions.append(e)
        return program
