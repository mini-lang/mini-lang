class Node():
    """
    A base node in the abstract syntax tree.
    """
    def __init__(self, name):
        """
        Initialize a node with a name
        """
        self.name = name

    def __str__(self):
        return self.name

class ProgramNode(Node):
    """
    A program node in the abstract syntax tree.
    """
    def __init__(self, expressions: list[Node]):
        """
        Initialize a program node with a list of expressions.
        """
        super().__init__("Program")
        self.expressions = expressions

class AtomicNode(Node):
    """
    An atomic expression node in the abstract syntax tree.
    """
    def __init__(self, valueType: str, value):
        """
        Initialize an atomic expression node with a value.
        """
        super().__init__("Atomic")
        self.valueType = valueType
        self.value = value

    def __str__(self):
        value = f"'{self.value}'" if self.valueType == "string" else str(self.value)
        return f"{self.valueType}({value})"

class BlockNode(Node):
    """
    A block node in the abstract syntax tree.
    """
    def __init__(self, expressions: list[Node]):
        """
        Initialize a block node with a list of expressions.
        """
        super().__init__("Block")
        self.expressions = expressions

    def __str__(self):
        return '{' + '; '.join(map(str, self.expressions)) + '}'

class TupleNode(Node):
    """
    A tuple node in the abstract syntax tree.
    """
    def __init__(self, elements: list[Node]):
        """
        Initialize a tuple node with a list of elements.
        """
        super().__init__("Tuple")
        self.elements = elements

    def __str__(self):
        return '(' + ", ".join(map(str, self.elements)) + ')'

class ListNode(Node):
    """
    A list node in the abstract syntax tree.
    """
    def __init__(self, elements: list[Node]):
        """
        Initialize a list node with a list of elements.
        """
        super().__init__("List")
        self.elements = elements

    def __str__(self):
        return '[' + ", ".join(map(str, self.elements)) + ']'

class MapNode(Node):
    """
    A hash map node in the abstract syntax tree.
    """
    def __init__(self, pairs: dict[Node, Node]):
        """
        Initialize a map node with a list of elements.
        """
        super().__init__("Map")
        self.pairs = pairs

    def __str__(self):
        return '{' + ', '.join(map(lambda t: f"{t[0]}: {t[1]}", self.pairs.items())) + '}'

class UnaryNode(Node):
    """
    A unary node in the abstract syntax tree.
    """
    def __init__(self, operator: str, rhs: Node):
        """
        Initialize a unary expression node with an operator and a right
        expression.
        """
        super().__init__("Unary")
        self.operator = operator
        self.rhs = rhs

    def __str__(self):
        return f"{self.operator}({self.rhs})"

class BinaryNode(Node):
    """
    A binary expression node in the abstract syntax tree.
    """
    def __init__(self, operator: str, left: Node, right: Node):
        """
        Initialize a binary expression node with an operator, left and right
        expressions.
        """
        super().__init__("Binary")
        self.operator = operator
        self.left = left
        self.right = right

    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"

class LambdaNode(Node):
    """
    A lambda function node in the abstract syntax tree.
    """
    def __init__(self, params: list[str], body: Node):
        """
        Initialize a lambda function node with a list of parameters and a body.
        """
        super().__init__("Lambda")
        self.params = params
        self.body = body

    def __str__(self):
        return f"({self.params} => {self.body})"

class IfNode(Node):
    """
    An if node in the abstract syntax tree.
    Contains a condition and body togehter with an optional if else statements and else body.
    """
    def __init__(self, condition: Node, ifBody: Node, elseIfs: list[tuple[Node, Node]] = [], elseBody: Node = None):
        """
        Initialize an if node with a condition, if body and an optional else body and else ifs.
        """
        super().__init__("If")
        self.condition = condition
        self.ifBody = ifBody
        self.elseBody = elseBody
        self.elseIfs = elseIfs
