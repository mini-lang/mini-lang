from io import TextIOBase

from .stdlib import init_stdlib

from .parser import Parser
from .lexer import Lexer
from .evaluator import evaluate
from .environment import Environment


def globalEnvironment():
    env = Environment("global", None)
    init_stdlib(env)
    return env

def execute(input: TextIOBase, env: Environment, debug = False):
    """Return (value, environment), or raise MiniError for a program error."""
    lexer = Lexer(input, debug)
    parser = Parser(lexer, debug)
    if debug:
        print("== Tokens ==")
    ast = parser.parse()
    if debug:
        print("== AST ==")
        print('  ' + '\n  '.join(str(e) for e in ast.expressions))
        print("== Evaluation ==")
    result = evaluate(ast, env, debug)
    if debug:
        print("== END ==")
        print("Result:", result, "//", result.type)
    return result, env # Return the result and the environment
