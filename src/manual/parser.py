# Parser class
from .lexer import Lexer, Token
from .ast import AtomicNode, BinaryNode, BlockNode, IfNode, LambdaNode, ListNode, MapNode, Node, ProgramNode, SliceNode, TupleNode, UnaryNode

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
    'PLUSEQUAL': 50,
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
        raise Exception(f"Semantic Error at {token.line}:{token.column}: {msg}")

    def __expect(self, token_name: str):
        """
        Expect a token from the lexer.
        """
        t = self.lexer.next_token()
        if t.name != token_name:
            raise Exception(f"Expected {token_name} but got {t.name}")
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
            if not (isinstance(e, AtomicNode) or e.type == "identifier"):
                raise Exception(f"Lambda argument '{e}' is not an identifier!")
            result.append(e.value)
        return result

    def __parse_primary(self) -> Node:
        """
        Parse a primary expression from the lexer.
        """
        prev_comment = self.lexer.prev_comment()
        t = self.lexer.next_token()
        if t.name in ["IDENTIFIER", "STRING", "NUMBER", "BOOL"]:
            value = AtomicNode(t.name.lower(), t.value)
            nt = self.lexer.peek_token()
            if nt.name == "RIGHTARROW":
                return self.__parse_lambda([value])
            else:
                return value
        elif t.name == "KEYWORD":
            match t.value:
                case "if": return self.__parse_if()
                case _: raise Exception(f"Keyword '{t.value}' is not implemented!")
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
            return UnaryNode(t.name, self.__parse_primary())
        else:
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
        body = self.__parse_expression()
        return LambdaNode(params, body)

    def __parse_binary_expression(self, lhs: Node, precedence: int) -> Node:
        """
        Parse a binary expression from the lexer.
        Should only be called from within `__parse_binary_expression` itself.
        Ref: https://en.wikipedia.org/wiki/Operator-precedence_parser#Pratt_parsing
        """
        l = self.lexer.peek_token().name
        while (l in precedence_left and precedence_left[l] >= precedence):
            op = self.lexer.next_token().name
            if op == "INDEX":
                self.__dprint(f"Parsing indexing expression")
                rhs = self.__parse_expression()
                # Check if range index
                if self.lexer.peek_token().name == "COLON":
                    self.lexer.next_token()
                    end = self.__parse_expression()
                    step = None
                    if self.lexer.peek_token().name == "COLON":
                        self.lexer.next_token()
                        step = self.__parse_expression()
                    rhs = SliceNode(rhs, end, step)
                self.__expect("RBRACKET")
            elif op == 'CALL':
                rhs = TupleNode(self.__parse_list_of_expressions("COMMA", "RPAREN", False))
                # if self.lexer.peek_token().name == "ASSIGNMENT":
                #     self.lexer.next_token() # Remove the assignment
                #     rhs = self.__parse_expression()
                #     # Convert args to list of strings
                #     args = self.__ident_list_to_str(args)
                #     return AssignmentNode(t.value, LambdaNode(args, rhs), prev_comment)
            else:
                rhs = self.__parse_primary()
            l = self.lexer.peek_token().name
            while l in precedence_left and precedence_left[l] > precedence_left[op]:
                rhs = self.__parse_binary_expression(rhs, precedence_left[l])
                l = self.lexer.peek_token().name
            lhs = BinaryNode(op, lhs, rhs)
        return lhs

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
                raise Exception(f"Duplicate key '{key}' in hash map!")
            pairs[key] = value
            nt = self.lexer.peek_token()
            if nt.name == "COMMA":
                self.lexer.next_token()
            elif nt.name != "RBRACE":
                self.__error(f"Expected 'COMMA' or 'RBRACE' but got '{nt.name}'", nt)
        self.lexer.next_token() # Remove the end delimiter
        return MapNode(pairs)

    def __parse_if(self) -> IfNode:
        """
        Parse an if expression from the lexer.
        """
        cond = self.__parse_expression()
        ifBody = self.__parse_expression()
        elseIfs = []
        elseBody = None
        nt = self.lexer.peek_token()
        while nt.name == "KEYWORD" and nt.value == "else":
            self.lexer.next_token() # Remove the else keyword
            # Peek and see if the next token is a chained if expression
            nt = self.lexer.peek_token()
            if nt.name == "KEYWORD" and nt.value == "if":
                self.lexer.next_token() # Remove the if keyword
                elseIfCond = self.__parse_expression()
                elseIfBody = self.__parse_expression()
                elseIfs.append((elseIfCond, elseIfBody))
            else:
                elseBody = self.__parse_expression()
                break
        return IfNode(cond, ifBody, elseIfs, elseBody)

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
