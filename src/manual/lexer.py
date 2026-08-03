from io import TextIOBase

# Token class
class Token():
    """
    The smallest unit of the language.
    """
    def __init__(self, name: str, line, column, value = None):
        """
        Initialize a token with a name and a value.
        """
        self.name = name
        self.value = value
        self.line = line
        self.column = column

    def __str__(self):
        """
        Return a string representation of the token.
        """
        return f"{self.name}: '{self.value}' at {self.line}:{self.column}"

# Lexer class
class Lexer:
    def __init__(self, source: TextIOBase, debug = False):
        self.__source = source
        self.__process_queue: list[str] = [] # FIFO Queue of chars that have been read but not yet processed
        self.__line = 1
        self.__column = 1
        self.__debug = debug
        self.__prev_char: str = None # Previously read character
        self.__peeked_token: Token | None = None # The last token that was peeked
        self.__prev_comment: Token | None = None # The last comment that was read before the previous token

    # Helper functions
    def __dprint(self, *args):
        """
        Print debug information.
        """
        if self.__debug:
            print(*args)
    def __token(self, name: str, value = None) -> Token:
        """
        Create a token with the given name and value.
        """
        return Token(name, self.__line, self.__column, value)

    def __error(self, msg: str):
        """
        Raise an error with the given message.
        """
        raise Exception(f"Syntax Error at {self.__line}:{self.__column}: {msg}")

    # Tokenizer functions
    def __can_read(self) -> bool:
        """
        Check if source can be read.

        Returns
        -------
        bool
            True if source can be read, False otherwise.
        """
        return self.__source.readable()

    def __queue_request(self, length: int):
        """
        Assert that the queue has at least the given length.
        If the queue is too short, read more characters from source
        until the queue is as long as the given length.

        Parameters
        ----------
        length : int
            The length to assert.
        """
        while len(self.__process_queue) < length:
            if not self.__can_read(): break
            c = self.__source.read(1)
            if c == '': break
            self.__process_queue.append(c)

    def __next_char(self):
        """
        Get the next character from source.

        Returns
        -------
        str | None
            The next character from the source stream.
            Or None if the end of the stream has been reached.
        """
        self.__queue_request(1)
        if len(self.__process_queue) == 0: return None
        c = self.__process_queue.pop(0)
        if c == '\n':
            self.__line += 1
            self.__column = 1
        elif c == '\t':
            self.__column += 4
        else:
            self.__column += 1
        self.__prev_char = c
        return c
    
    def __expect_char(self, expected: str):
        """
        Assert that the next character from source is the expected character.

        Parameters
        ----------
        expected : str
            The expected character.
        """
        c = self.__next_char()
        if c == None: self.__error(f"Expected {expected} but got EOF")
        return c

    def __peek_char(self, offset = 0) -> str:
        """
        Get the next character from source without consuming it from the stream.

        Parameters
        ----------
        offset : int
            The offset from the current position.

        Returns
        -------
        str
            The next character from the source stream.
            Or '\\0' if the end of the stream has been reached.
        """
        self.__queue_request(1 + offset)
        return self.__process_queue[offset] if len(self.__process_queue) > offset else '\0'

    def __read_string(self, quote: str) -> Token:
        """
        Read a string from source.

        Parameters
        ----------
        quote : str
            The quote character.

        Returns
        -------
        Token
            A token with the string value.
        """
        s = ""
        while self.__can_read():
            c = self.__expect_char("string content, escape sequence, or closing quote")
            if c == quote:
                return self.__token("STRING", s)
            elif c == '\\':
                c = self.__expect_char("string escape sequence")
                if c == 'n':
                    s += '\n'
                elif c == 't':
                    s += '\t'
                elif c == 'r':
                    s += '\r'
                elif c == '\\':
                    s += '\\'
                elif c in ['"', "'"]:
                    s += c
                else:
                    self.__error("Invalid escape sequence: \\" + c)
            else:
                s += c
        self.__error("Unterminated string")

    def __read_identifier(self, first: str) -> Token:
        """
        Read an identifier from source.

        Returns
        -------
        Token
            A token with the identifier value.
        """
        s = first
        nc = self.__peek_char()
        while nc.isalnum() or nc == '_':
            s += self.__expect_char("identifier character")
            if self.__can_read():
                nc = self.__peek_char()
            else:
                break
        return self.__token("IDENTIFIER", s)

    def __read_number(self, first: str) -> Token:
        """
        Read a number from source.

        Returns
        -------
        Token
            A token with the number value.
        """
        s = first
        decimalPoint = False
        nc = self.__peek_char()
        nnc = self.__peek_char(1)
        while (nc.isdigit() or nc == '.') and not (nc == '.' and nnc == '.'):
            if nc == '.':
                if decimalPoint:
                    break
                decimalPoint = True
            s += self.__expect_char("digit or decimal point")
            if self.__can_read():
                nc = self.__peek_char()
            else:
                break
        value = float(s)
        value = int(value) if value.is_integer() else value
        return self.__token("NUMBER", value)

    def __is_end_of_expression(self, c: str) -> bool:
        return (c is not None) and (c.isalnum() or c in ['_', ']', '}', ')'])

    def __read_token(self) -> Token:
        """
        Tokenize the next character from source.

        Returns
        -------
        Token
            The next token from the source stream.
        """
        pc = self.__prev_char
        c = self.__next_char()
        if c in ['', '\0', None]: return self.__token("EOF")
        nc = self.__peek_char() # Look ahead one character: LL(1)

        # Whitespace
        if c in [' ', '\t', '\n', '\r']:
            return self.__read_token() # Skip whitespace
        if c in ['"', "'"]:
            return self.__read_string(c)
        if c.isdigit():
            return self.__read_number(c)
        if c.isalpha() or c == '_':
            t = self.__read_identifier(c)
            if t.value in ["true", "false"]:
                return self.__token("BOOL", t.value == "true")
            if t.value in ["if", "else", "match", "class", "enum", "while", "for", "break", "continue", "return"]:
                return self.__token("KEYWORD", t.value)
            if t.value in ["and", "or", "not", "is", "in"]:
                return self.__token(t.value.upper(), t.value)
            return t
        if c == '/' and nc == '/':
            self.__expect_char("single line comment start")
            comment = ""
            while self.__can_read() and self.__peek_char() != '\n':
                comment += self.__expect_char("comment content")
            return self.__token("COMMENT", comment)
        if c == '/' and nc == '*':
            self.__expect_char("multi line comment start")
            comment = ""
            while self.__can_read():
                c = self.__expect_char("comment content")
                if c == '*' and self.__peek_char() == '/':
                    self.__expect_char("multi line comment end")
                    break
                comment += c
            return self.__token("COMMENT", comment)
        # Operators
        if c == '+' and nc == '=': return self.__token("PLUSEQUAL", c + self.__next_char())
        if c == '-' and nc == '=': return self.__token("MINUSEQUAL", c + self.__next_char())
        if c == '*' and nc == '=': return self.__token("TIMESEQUAL", c + self.__next_char())
        if c == '/' and nc == '=': return self.__token("DIVEQUAL", c + self.__next_char())
        if c == '%' and nc == '=': return self.__token("MODEQUAL", c + self.__next_char())
        if c == '^' and nc == '=': return self.__token("POWEQUAL", c + self.__next_char())
        if c == '<' and nc == '=': return self.__token("LESSEQUAL", c + self.__next_char())
        if c == '>' and nc == '=': return self.__token("GREATEREQUAL", c + self.__next_char())
        if c == '!' and nc == '=': return self.__token("NOTEQUAL", c + self.__next_char())
        if c == '=' and nc == '=': return self.__token("EQUAL", c + self.__next_char())
        if c == '=' and nc == '>': return self.__token("RIGHTARROW", c + self.__next_char())
        if c == '&' and nc == '&': return self.__token("AND", c + self.__next_char())
        if c == '|' and nc == '|': return self.__token("OR", c + self.__next_char())
        if c == '#' and nc == '{': return self.__token("HASHBRACE", c + self.__next_char())
        if c == '.' and nc == '.': return self.__token("RANGE", c + self.__next_char())
        if c == '+': return self.__token("PLUS", c)
        if c == '-': return self.__token("MINUS", c)
        if c == '*': return self.__token("MULTIPLY", c)
        if c == '/': return self.__token("DIVIDE", c)
        if c == '%': return self.__token("MODULO", c)
        if c == '^': return self.__token("POWER", c)
        if c == '<': return self.__token("LESS", c)
        if c == '>': return self.__token("GREATER", c)
        if c == '=': return self.__token("ASSIGNMENT", c)
        if c == '!': return self.__token("NOT", c)
        if c == '&': return self.__token("BITWISEAND", c)
        if c == '|': return self.__token("BITWISEOR", c)
        if c == '~': return self.__token("BITWISENOT", c)
        if c == '?': return self.__token("QUESTIONMARK", c)
        if c == '.': return self.__token("DOT", c)
        if c == ',': return self.__token("COMMA", c)
        if c == ':': return self.__token("COLON", c)
        if c == ';': return self.__token("SEMICOLON", c)
        if c == '{': return self.__token("LBRACE", c)
        if c == '}': return self.__token("RBRACE", c)
        if c == '(':
            if self.__is_end_of_expression(pc):
                return self.__token("CALL", c) # Treat as a function call
            return self.__token("LPAREN", c) # Normal parenthesis
        if c == ')': return self.__token("RPAREN", c)
        if c == '[':
            if self.__is_end_of_expression(pc):
                return self.__token("INDEX", c) # Indexing
            return self.__token("LBRACKET", c) # Normal bracket
        if c == ']': return self.__token("RBRACKET", c)
        self.__error("Unexpected character: " + c)

    def is_done(self):
        """
        Check if the lexer is done.

        Returns
        -------
        bool
            True if the lexer is done, False otherwise.
        """
        return not self.__can_read() or self.peek_token().name == "EOF"

    def reset_peek(self):
        """
        Reset the peek token.
        """
        self.__peeked_token = None

    def peek_token(self, allow_comment = False) -> Token:
        """
        Peek at the next token.

        Returns
        -------
        Token
            The next token.
        """
        if self.__peeked_token is not None:
            return self.__peeked_token
        else:
            t = self.next_token(allow_comment)
            self.__peeked_token = t
            return t

    def next_token(self, allow_comment = False) -> Token:
        """
        Get the next token from the source.

        Returns
        -------
        Token
            The next token from the source.
        """
        if self.__peeked_token is not None:
            t = self.__peeked_token
            self.reset_peek()
            return t
        else:
            t = self.__read_token()
            if not allow_comment and t.name == "COMMENT":
                self.__prev_comment = t
                return self.next_token(False)
            self.__dprint("  " + str(t))
            return t

    def prev_comment(self):
        return self.__prev_comment
