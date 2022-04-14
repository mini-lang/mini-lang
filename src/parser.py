# Parser class
from .lexer import Lexer, Token
from .ast import AssignmentNode, AtomicNode, BinaryNode, FunctionCallNode, IndexingNode, LambdaFunctionNode, ListNode, Node, ProgramNode, TupleNode, UnaryNode

# Left associative infix operators binding powers
precedence_binary_left = {
    'POWER':    30,
    'NOT':      30,
    'MULTIPLY': 20,
    'DIVIDE':   20,
    'MODULO':   20,
    'PLUS':     10,
    'MINUS':    10,
    'EQUAL':    5,
}

# Right associative infix operators binding powers
precedence_binary_right = {
    'AND':      20,
    'OR':       10,
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
    def __parse_list_of_expressions(self, delimiter: str, end_delimiter: str) -> list[Node]:
        """
        Parse a list of expressions from the lexer and return them as a list.
        The expressions are separated by the given delimiter and the list ends with the given end delimiter.
        No start delimiter is required.
        """
        expressions = []
        nt = self.lexer.peek_token()
        while nt.name != end_delimiter:
            expressions.append(self.__parse_expression())
            nt = self.lexer.peek_token()
            if nt.name == delimiter:
                self.lexer.next_token()
            elif nt.name != end_delimiter:
                self.__error(f"Expected '{delimiter}' or '{end_delimiter}' but got '{nt.name}'", nt)
        self.lexer.next_token() # Remove the end delimiter
        return expressions

    def __parse_primary(self) -> Node:
        """
        Parse a primary expression from the lexer.
        """
        t = self.lexer.next_token()
        if t.name == "IDENTIFIER":
            nt = self.lexer.peek_token()
            if nt.name == 'LPAREN':
                self.lexer.next_token() # Remove the opening paren
                args = self.__parse_list_of_expressions("COMMA", "RPAREN")
                return FunctionCallNode(t.value, args)
            elif nt.name == 'LBRACKET':
                self.lexer.next_token() # Remove the opening bracket
                index = self.__parse_expression()
                self.__expect("RBRACKET")
                return IndexingNode(AtomicNode("identifier", t.value), index)
            elif nt.name == 'ASSIGNMENT':
                self.lexer.next_token() # Remove the assignment operator
                rhs = self.__parse_expression()
                return AssignmentNode(t.value, rhs)
            else:
                return AtomicNode("identifier", t.value)
        elif t.name in ["STRING", "NUMBER", "BOOLEAN"]:
            return AtomicNode(t.name.lower(), t.value)
        elif t.name == "KEYWORD":
            raise Exception(f"Keyword '{t.value}' is not implemented!")
        elif t.name == "LPAREN":
            lhs = TupleNode(self.__parse_list_of_expressions("COMMA", "RPAREN"))
            # Check for trailing right arrow
            nt = self.lexer.peek_token()
            if nt.name == "RIGHTARROW":
                self.lexer.next_token() # Remove right arrow
                # Validate that the tuple only has identifiers
                # And add them to a list of argument names
                args = []
                for e in lhs.elements:
                    if not (isinstance(e, AtomicNode) or e.name == "IDENTIFIER"):
                        raise Exception(f"Lambda argument '{e}' is not an identifier!")
                    args.append(e.value)
                # Parse the body of the lambda
                body = self.__parse_expression()
                return LambdaFunctionNode(args, body)
            else:
                return lhs
        elif t.name == "LBRACKET":
            return ListNode(self.__parse_list_of_expressions("COMMA", "RBRACKET"))
        elif t.name in ["MINUS", "NOT"]:
            return UnaryNode(t.name, self.__parse_expression())
        else:
            self.__error(f"Expected primary expression but got '{t.name}'", t)

    def __parse_binary_expression(self, lhs: Node, precedence: int) -> Node:
        """
        Parse a binary expression from the lexer.

        Should only be called from within `__parse_binary_expression` itself.

        Ref: https://en.wikipedia.org/wiki/Operator-precedence_parser#Pratt_parsing
        """
        l = self.lexer.peek_token().name
        while ((l in precedence_binary_left and precedence_binary_left[l] >= precedence) or
               (l in precedence_binary_right and precedence_binary_right[l] > precedence)):
            op = self.lexer.next_token().name
            self.__dprint(f"Parsing binary expression with operator '{op}'")
            rhs = self.__parse_primary()
            l = self.lexer.peek_token().name
            while ((l in precedence_binary_left and precedence_binary_left[l] > precedence_binary_left[op]) or
                   (l in precedence_binary_right and precedence_binary_right[l] == precedence_binary_right[op])):
                rhs = self.__parse_binary_expression(rhs, precedence_binary_left[l])
                l = self.lexer.peek_token().name
            lhs = BinaryNode(op, lhs, rhs)
        return lhs

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
            self.__dprint(f"Parsed expression: {e}")
            program.expressions.append(e)
        self.__dprint(f"Parsed program: {program}")
        return program
