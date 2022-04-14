# Fundamental value types in the language
from typing import Callable

from .ast import Node

class Atom():
    """
    A fundamental value type in the language.
    """
    def __init__(self, name, type):
        """
        Initialize an atom with a name and a type.
        """
        self.name = name
        self.type = type

    def __str__(self):
        return f"<{self.type}>"

class ValueAtom(Atom):
    """
    An atomic value node in the abstract syntax tree.
    """
    def __init__(self, valueType: str, value):
        """
        Initialize an atomic value node with a value.

        Parameters
        ----------
            valueType: The type of the value in lower case.
                       E.g. "string", "number", "boolean", "unit", "tuple", "list".
            value: The value of the node.
        """
        super().__init__("Value", valueType)
        self.valueType = valueType
        self.value = value

    def listValueToStr(self):
        return list(map(lambda a: str(a), self.value))

    def __str__(self) -> str:
        value = str(self.value)
        if self.valueType == "string":
            return f"'{value}'"
        elif self.valueType == "boolean":
            return value.lower()
        elif self.valueType == "unit":
            return "()"
        elif self.valueType == "tuple":
            return '(' + ", ".join(self.listValueToStr()) + ')'
        elif self.valueType == "list":
            return '[' + ", ".join(self.listValueToStr()) + ']'
        elif self.valueType == "number" and self.value.is_integer():
            return str(int(self.value))
        return value

    def __repr__(self) -> str:
        value = str(self.value)
        if self.valueType == "boolean":
            return value.lower()
        elif self.valueType == "unit":
            return "()"
        elif self.valueType == "tuple":
            return '(' + ", ".join(self.listValueToStr()) + ')'
        elif self.valueType == "list":
            return '[' + ", ".join(self.listValueToStr()) + ']'
        elif self.valueType == "number" and self.value.is_integer():
            return str(int(self.value))
        return value

class FunctionAtom(Atom):
    """
    A function node in the abstract syntax tree.
    """
    def __init__(self, argumentNames: list[str], body: Node, environment):
        """
        Initialize a function node with a function name, argument names, body and the environment in which it was defined.
        """
        super().__init__("Function", "function")
        self.argumentNames = argumentNames
        self.body = body
        self.environment = environment

    def __str__(self):
        return f"<lambda({', '.join(self.argumentNames)})>"

class BuiltinFunctionAtom(Atom):
    """
    A builtin function node in the abstract syntax tree.
    """
    def __init__(self, functionName: str, func: Callable):
        """
        Initialize a builtin function node with a function name and a function.
        """
        super().__init__("Built-in function", "function")
        self.functionName = functionName
        self.func = func

    def __str__(self):
        return f"<built-in: {self.functionName}>"
