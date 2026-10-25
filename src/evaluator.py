from .atoms import Atom, BuiltinFunctionAtom, FunctionAtom, ValueAtom
from .ast import AtomicNode, BinaryNode, BlockNode, IfNode, LambdaNode, ListNode, MapNode, Node, ProgramNode, SliceNode, TupleNode, UnaryNode, WhileNode, ForNode, ControlNode
from .environment import Environment

# Global variables
debug = False

# Helper functions
def dprint(*args):
    """
    Print debug messages.
    """
    if debug:
        print(*args)

def compatible_types(lhs: Atom, rhs: Atom, types: list[str]) -> bool:
    """
    Check if the two atoms are compatible with the given types.
    """
    if not isinstance(lhs, ValueAtom):
        raise Exception(f"Left hand side in expression is not an atomic value")
    if not isinstance(rhs, ValueAtom):
        raise Exception(f"Right hand side in expression is not an atomic value")
    if lhs.type in types and rhs.type in types:
        return True
    else:
        raise Exception(f"Incompatible types: {lhs.type} and {rhs.type}")

def compatible_type(value: Atom, types: list[str]) -> bool:
    """
    Check if the given value is a `ValueAtom` and compatible with the given types.
    """
    if not isinstance(value, ValueAtom):
        raise Exception(f"Value is not an atomic value")
    if value.type in types:
        return True
    else:
        raise Exception(f"Incompatible types: {value.type} and {types}")

def is_identifier(expression: Node) -> bool:
    return isinstance(expression, AtomicNode) and expression.type == "identifier"

def is_identifier_members(expression: Node) -> bool:
    return isinstance(expression, BinaryNode) and expression.operator == "DOT" and (
        is_identifier(expression.left) or is_identifier_members(expression.left)
    ) and is_identifier(expression.right)

def is_index_expression(expression: Node) -> bool:
    return isinstance(expression, BinaryNode) and expression.operator == "INDEX"

def get_left_most_bin_term(expression: Node, op: str) -> Node:
    """
    Get the base of a member expression.
    """
    if isinstance(expression, BinaryNode) and expression.operator == op:
        return get_left_most_bin_term(expression.left, op)
    else:
        return expression

def flatten_bin_terms(expression: Node, op: str, includeBase: bool) -> list[str]:
    """
    Get the path of a member expression.
    """
    if isinstance(expression, BinaryNode) and expression.operator == op:
        return flatten_bin_terms(expression.left, op, includeBase) + [expression.right.value]
    else:
        return [expression.value] if includeBase else []

def set_nested_value(obj: ValueAtom, path: list[str], rhs: Atom) -> ValueAtom:
    """
    Set the value of a member expression.
    """
    if len(path) == 0: raise Exception("Member path is empty")
    elif len(path) == 1:
        obj.value[path[0]] = rhs
        return obj
    else:
        obj.value[path[0]] = set_nested_value(obj.value[path[0]], path[1:], rhs)
        return obj

class LoopControl(Exception):
    def __init__(self, kind: str):
        self.kind = kind


class ReturnControl(Exception):
    def __init__(self, value: Atom):
        self.value = value


def condition_value(expression: Node, env: Environment) -> bool:
    value = evaluate_expression(expression, env)
    if not isinstance(value, ValueAtom) or value.type != "bool":
        raise Exception("Condition must evaluate to a bool")
    return value.value


def iteration_values(value: Atom):
    if isinstance(value, ValueAtom):
        if value.type in ["list", "tuple"]:
            return iter(value.value)
        if value.type in ["string", "map"]:
            return (ValueAtom("string", item) for item in value.value)
        if value.type == "unit":
            return iter(())
    raise Exception("For loop expects a list, tuple, string or map")


# Evaluation functions

def evaluate_expression(expression: Node, env: Environment) -> Atom:
    if isinstance(expression, AtomicNode):
        if is_identifier(expression):
            dprint(f"Evaluating identifier '{expression.raw_str()}'")
            val = env.get(expression.value)
            if val is None:
                raise Exception(f"identifier '{expression.value}' is not defined")
            return val
        else:
            return ValueAtom(expression.type, expression.value)
    elif isinstance(expression, TupleNode):
        if len(expression.elements) == 0:
            return ValueAtom("unit", None)
        elif len(expression.elements) == 1:
            return evaluate_expression(expression.elements[0], env)
        else:
            return ValueAtom("tuple", list(map(lambda e: evaluate_expression(e, env), expression.elements)))
    elif isinstance(expression, ListNode):
        return ValueAtom("list", list(map(lambda e: evaluate_expression(e, env), expression.elements)))
    elif isinstance(expression, MapNode):
        map_values: dict[str, Atom] = {}
        for key, value in expression.pairs.items():
            if not isinstance(key, AtomicNode):
                raise Exception(f"Key in map is not an atomic value")
            if key.type == "number" and (isinstance(key.value, int) or key.value.is_integer()):
                key.value = int(key.value)
                key.type = "integer"
            if key.type not in ["identifier", "string", "integer", "bool"]:
                raise Exception(f"Key in map is not an identifier, string, integer or bool")
            value = evaluate_expression(value, env)
            map_values[str(key.value)] = value
        return ValueAtom("map", map_values)
    elif isinstance(expression, BlockNode):
        return evaluate_expressions(expression.expressions, Environment(f"<block>", env))
    elif isinstance(expression, LambdaNode):
        return FunctionAtom(expression.params, expression.body, env)
    elif isinstance(expression, IfNode):
        if condition_value(expression.condition, env):
            return evaluate_expression(expression.ifBody, env)
        for condition, body in expression.elseIfs:
            if condition_value(condition, env):
                return evaluate_expression(body, env)
        if expression.elseBody is not None:
            return evaluate_expression(expression.elseBody, env)
        return ValueAtom("unit", None)
    elif isinstance(expression, WhileNode):
        while condition_value(expression.condition, env):
            try:
                evaluate_expression(expression.body, Environment("<while>", env))
            except LoopControl as signal:
                if signal.kind == "break":
                    break
        return ValueAtom("unit", None)
    elif isinstance(expression, ForNode):
        values = iteration_values(evaluate_expression(expression.iterable, env))
        for value in values:
            iteration = Environment("<for>", env)
            iteration.define(expression.variable, value)
            try:
                evaluate_expression(expression.body, iteration)
            except LoopControl as signal:
                if signal.kind == "break":
                    break
        return ValueAtom("unit", None)
    elif isinstance(expression, ControlNode):
        if expression.kind == "return":
            raise ReturnControl(evaluate_expression(expression.value, env))
        raise LoopControl(expression.kind)
    elif isinstance(expression, UnaryNode):
        op = expression.operator
        rhs = evaluate_expression(expression.rhs, env)
        if op == "MINUS" and compatible_type(rhs, ["number"]):
            return ValueAtom("number", -rhs.value)
        elif op == "NOT" and compatible_type(rhs, ["bool"]):
            return ValueAtom("bool", not rhs.value)
        else:
            raise Exception(f"Unkown unary operator '{op}'")
    elif isinstance(expression, BinaryNode):
        op = expression.operator

        if op == "ASSIGNMENT":
            dprint(f"Evaluating assignment {expression.left.formatted_str()} = {expression.right.formatted_str()}")
            if is_identifier(expression.left):
                rhs = evaluate_expression(expression.right, env)
                env.set(expression.left.value, rhs)
                return rhs
            elif is_identifier_members(expression.left) or is_index_expression(expression.left):
                op = "DOT" if is_identifier_members(expression.left) else "INDEX"
                rhs = evaluate_expression(expression.right, env)
                base = get_left_most_bin_term(expression.left, op)
                if is_identifier(base):
                    obj = env.get(base.value)
                    if obj is None: raise Exception(f"Object '{base.value}' is not defined")
                    path = flatten_bin_terms(expression.left, op, False)
                    obj = set_nested_value(obj, path, rhs)
                    env.set(base.value, obj)
                    return rhs
                else:
                    raise Exception(f"Cannot set member of non-identifer values")
            elif isinstance(expression.left, BinaryNode) and expression.left.operator == "CALL":
                # Function declaration 
                functionName = expression.left.left
                if not is_identifier(functionName):
                    raise Exception(f"Function name is not an identifier")
                args = expression.left.right
                # Check that the arguments is a a tuple of identifiers
                if not isinstance(args, TupleNode):
                    raise Exception(f"Function arguments are not a tuple")
                argNames: list[str] = []
                for a in args.elements:
                    if not isinstance(a, AtomicNode) or a.type != "identifier":
                        raise Exception(f"Function argument '{a}' is not an identifier")
                    argNames.append(a.value)
                # Assign the right hand side as body of the function
                body = expression.right
                value = FunctionAtom(argNames, body, env, functionName.value)
                # Update the environment
                env.set(functionName.value, value)
                return value
            else:
                raise Exception(f"Invalid assignment, left hand side is not an identifier, function or valid pattern")

        lhs = evaluate_expression(expression.left, env)
        if op == "DOT":
            # Member access, last identifier is the member name and the rest is the object
            dprint(f"Evaluating member access {lhs.formatted_str()}.{expression.right.formatted_str()} ({expression.right.__class__})")
            if not is_identifier(expression.right):
                raise Exception(f"Cannot access member of {lhs.type} with non-identifier key")
            if not (isinstance(lhs, ValueAtom) and lhs.type in ["map", "tuple", "list"]):
                raise Exception(f"Cannot access member of {lhs.type}")
            if lhs.type == "map":
                if expression.right.value not in lhs.value:
                    raise Exception(f"Map does not contain key '{expression.right.value}'")
                return lhs.value[expression.right.value]
            raise Exception(f"Cannot access member of {lhs.type}, not implemented yet")
        elif op == "CALL":
            # Preserve argument boundaries: f((1, 2)) has one tuple argument.
            args = [evaluate_expression(arg, env) for arg in expression.right.elements]
            return evaluate_call(lhs, args)
        elif op in ["AND", "OR"]:
            compatible_type(lhs, ["bool"])
            if (op == "AND" and not lhs.value) or (op == "OR" and lhs.value):
                return lhs
            rhs = evaluate_expression(expression.right, env)
            compatible_type(rhs, ["bool"])
            return rhs
        elif op == "INDEX" and isinstance(expression.right, SliceNode): # Slice indexing
            # Evaluate the slice indices
            start = evaluate_expression(expression.right.start, env)
            end = evaluate_expression(expression.right.end, env)
            step = ValueAtom("number", 1)
            if expression.right.step is not None:
                step = evaluate_expression(expression.right.step, env)
            # Check that the slice indices are integers
            if not compatible_types(start, end, ["number"]) or not compatible_type(step, ["number"]):
                raise Exception(f"Slice indices must be integers")
            start, end, step = int(start.value), int(end.value), int(step.value)
            if compatible_type(lhs, ["list", "tuple"]):
                lhs_slice = lhs.value[start:end:step]
                element = None
                if lhs.type == "list": element = ValueAtom("list", lhs_slice)
                elif lhs.type == "tuple": element = ValueAtom("tuple", lhs_slice)
                else: raise Exception(f"Cannot slice index {lhs.type}")
                dprint(f"Indexing {lhs.type}: {lhs.formatted_str()} with slice {start}:{end}:{step} -> {element.formatted_str()}")
                return element

        rhs = evaluate_expression(expression.right, env)
        # The rest of the operators rely on the right hand side being evaluated first
        # Try to evaluate binary operators first
        binOpResult = evaluate_binary_atom_expression(op, lhs, rhs, env)
        if binOpResult is not None:
            return binOpResult
        if op == "PLUSEQUAL" and compatible_types(lhs, rhs, ["string", "number"]):
            if not is_identifier(expression.left):
                raise Exception(f"Left hand side of mutating assignment operator '{op}' must be an identifier")
            if lhs.type == "string" or rhs.type == "string":
                new_value = ValueAtom("string", lhs.raw_str() + rhs.raw_str())
            else:
                new_value = ValueAtom("number", lhs.value + rhs.value)
            env.set(expression.left.value, new_value)
            return new_value

        raise Exception(f"Unknown binary operator '{op}'")
    else:
        raise Exception(f"Unknown expression type '{type(expression)}'")

def evaluate_binary_atom_expression(op: str, lhs: Atom, rhs: Atom, env: Environment) -> Atom:
    dprint(f"Evaluating binary expression {lhs.formatted_str()} {op} {rhs.formatted_str()}")
    if op == "PLUS" and compatible_types(lhs, rhs, ["string", "number", "bool", "list", "tuple", "map"]):
        if lhs.type == "string" or rhs.type == "string":
            return ValueAtom("string", lhs.raw_str() + rhs.raw_str())
        elif lhs.type == "list" and rhs.type == "list":
            return ValueAtom("list", lhs.value + rhs.value)
        elif lhs.type == "number" and rhs.type == "number":
            return ValueAtom("number", lhs.value + rhs.value)
        elif lhs.type == "tuple" and rhs.type == "tuple":
            # Ensure that the tuples have the same length
            if len(lhs.value) != len(rhs.value):
                raise Exception(f"Tuple size mismatch: {len(lhs.value)} and {len(rhs.value)}")
            new_value = map(lambda e: evaluate_binary_atom_expression("PLUS", e[0], e[1], env), zip(lhs.value, rhs.value))
            return ValueAtom("tuple", list(new_value))
        elif lhs.type == "map" and rhs.type == "map":
            # Concate the maps
            return ValueAtom("map", {**lhs.value, **rhs.value})
        else:
            raise Exception(f"Cannot add {lhs.type} and {rhs.type}")
    elif op == "MINUS" and compatible_types(lhs, rhs, ["number"]):
        return ValueAtom("number", lhs.value - rhs.value)
    elif op == "MULTIPLY" and compatible_types(lhs, rhs, ["number"]):
        return ValueAtom("number", lhs.value * rhs.value)
    elif op == "DIVIDE" and compatible_types(lhs, rhs, ["number"]):
        return ValueAtom("number", lhs.value / rhs.value)
    elif op == "MODULO" and compatible_types(lhs, rhs, ["number"]):
        return ValueAtom("number", lhs.value % rhs.value)
    elif op == "POWER" and compatible_types(lhs, rhs, ["number"]):
        return ValueAtom("number", lhs.value ** rhs.value)
    elif op == "EQUAL" and compatible_types(lhs, rhs, ["number", "string", "bool", "unit", "tuple", "list", "map"]):
        if lhs.type != rhs.type:
            return ValueAtom("bool", False)
        return ValueAtom("bool", lhs.value == rhs.value)
    elif op == "NOTEQUAL" and compatible_types(lhs, rhs, ["number", "string", "bool"]):
        return ValueAtom("bool", lhs.value != rhs.value)
    elif op == "LESS" and compatible_types(lhs, rhs, ["number"]):
        return ValueAtom("bool", lhs.value < rhs.value)
    elif op == "GREATER" and compatible_types(lhs, rhs, ["number"]):
        return ValueAtom("bool", lhs.value > rhs.value)
    elif op == "LESSEQUAL" and compatible_types(lhs, rhs, ["number"]):
        return ValueAtom("bool", lhs.value <= rhs.value)
    elif op == "GREATEREQUAL" and compatible_types(lhs, rhs, ["number"]):
        return ValueAtom("bool", lhs.value >= rhs.value)
    elif op == "AND" and compatible_types(lhs, rhs, ["bool"]):
        return ValueAtom("bool", lhs.value and rhs.value)
    elif op == "OR" and compatible_types(lhs, rhs, ["bool"]):
        return ValueAtom("bool", lhs.value or rhs.value)
    elif op == "RANGE" and compatible_types(lhs, rhs, ["number"]):
        return ValueAtom("list", [ValueAtom("number", i) for i in range(lhs.value, rhs.value)])
    elif op == "INDEX" and compatible_type(lhs, ["list", "tuple", "map"]):
        if not isinstance(rhs, ValueAtom):
            raise Exception(f"Indexing expression in not a valid value type: {rhs}")
        if rhs.type in ["number", "string", "bool"]:
            if lhs.type == "list" or lhs.type == "tuple":
                element: Atom = lhs.value[rhs.value]
            elif lhs.type == "map":
                index = rhs.raw_str()
                if index not in lhs.value:
                    print(lhs.value)
                    raise Exception(f"Map does not contain key '{index}'")
                element: Atom = lhs.value[index]
            dprint(f"Indexing {lhs.type}: {lhs.formatted_str()} with index {rhs.formatted_str()} -> {element.formatted_str()}")
            return element
        else:
            raise Exception(f"Indexing expression does not evaluate to an integer or string")

    return None

def evaluate_call(function: FunctionAtom | BuiltinFunctionAtom, args: list[Atom]) -> Atom:
    if isinstance(function, FunctionAtom):
        return evaluate_function_atom_call(function, args)
    elif isinstance(function, BuiltinFunctionAtom):
        return function.func(args) # Call the builtin function
    else:
        raise Exception(f"Cannot call non-function: {function}")

def evaluate_function_atom_call(function: FunctionAtom, args: list[Atom]) -> Atom:
    # Build a new environment for the function call
    # where the arguments are bound to the parameters
    funcEnv = Environment(f"<function {function.name}>", function.environment)
    if len(args) != len(function.argumentNames):
        raise Exception(f"Function '{function.name}' expects {len(function.argumentNames)} arguments, but got {len(args)}")
    for name, val in zip(function.argumentNames, args):
        funcEnv.define(name, val)
    try:
        return evaluate_expression(function.body, funcEnv)
    except ReturnControl as signal:
        return signal.value
    except LoopControl as signal:
        # Defensive boundary for ASTs supplied through the embedding API.
        raise Exception(f"'{signal.kind}' cannot cross a function boundary") from None

def evaluate_expressions(expressions: list[Node], env: Environment) -> Atom:
    """
    Evaluate a list of expressions and return the last result.
    """
    result = ValueAtom("unit", None)
    for expression in expressions:
        result = evaluate_expression(expression, env)
    return result

# Evaluator function
def evaluate(program: ProgramNode, env: Environment, _debug = False) -> Atom:
    """
    Evaluate a program node.
    """
    global debug
    debug = _debug
    return evaluate_expressions(program.expressions, env)
