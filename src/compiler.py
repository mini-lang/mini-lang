from io import TextIOBase, open
import os
from llvmlite import ir, binding

from .options import Options

from .ast import AtomicNode, IfNode, Node, ProgramNode
from .parser import Parser
from .lexer import Lexer


def compileFile(filepath: str, options: Options):
    with open(filepath, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True) as f:
        program = compile(f, options)

    # All these initializations are required for code generation!
    binding.initialize()
    binding.initialize_native_target()
    binding.initialize_native_asmprinter()

    # Create a target machine representing the host
    target = binding.Target.from_default_triple()
    target_machine = target.create_target_machine()
    obj = target_machine.emit_object(program)
    print(obj)
    # Save the generated code to a file
    with open(filepath + ".o", mode='w', buffering=-1, encoding=None, errors=None, newline=None, closefd=True) as f:
        f.write(obj)
    target_machine.close()
    print("Building executable...")
    # Build the executable
    binding.link_in_file(filepath + ".o")
    # Run GCC
    filename_path = os.path.splitext(filepath)[0]
    if os.system("gcc -o " + filename_path + " " + filepath + ".o") != 0:
        print("Compilation failed!")
    else:
        print("Done!")

# Types

bitTy = ir.IntType(1)
boolTy = ir.IntType(1)
int8Ty = ir.IntType(8)
charTy = ir.IntType(8)
int32Ty = ir.IntType(32)
int64Ty = ir.IntType(64)
floatTy = ir.FloatType()
doubleTy = ir.DoubleType()
# stringTy = charTy.as_pointer()

# Globals

module = None
builder = None

def compile(input: TextIOBase, options: Options) -> ir.Module:
    global module, builder
    print("Compiling...")
    lexer = Lexer(input, options.debug)
    parser = Parser(lexer, options.debug)
    ast = parser.parse()
    # LLVM IR
    module = ir.Module("program")
    builder = ir.IRBuilder()
    # https://clang.llvm.org/docs/CrossCompilation.html#target-triple
    module.triple = "x86_64-pc-linux-gnu"

    # generate(ast)



    # TODO: Log statistics, performance analysis and benchmarks of compilation
    print("Generated module:")
    print(module)
    return module


def generate(ast: Node):
    global builder
    if isinstance(ast, ProgramNode):
        # builder.append_basic_block("main")
        for n in ast.expressions:
            generate(n)
        # return builder.ret_void()
    elif isinstance(ast, AtomicNode):
        return generateAtomic(ast)
    elif isinstance(ast, IfNode):
        builder = ir.IRBuilder()
        pred = generate(ast.condition)
        with builder.if_else(pred) as (if_block, else_block):
            with if_block:
                generate(ast.if_body)
            with else_block:
                generate(ast.else_body)
    else:
        pass # raise Exception("Unknown AST node: " + str(ast))

def generateAtomic(ast: Node) -> ir.Value:
    if isinstance(ast, AtomicNode):
        if ast.valueType == "number":
            return ir.Constant(int32Ty if ast.value.is_integer() else floatTy, ast.value)
        elif ast.valueType == "bool":
            return ir.Constant(boolTy, 1 if ast.value else 0)
        elif ast.valueType == "unit":
            return ir.Undefined
        elif ast.valueType == "string":
            return ir.Constant(ir.ArrayType(charTy, len(ast.value)), bytearray(ast.value.encode("utf-8")))
        else:
            raise Exception("Unknown atomic type: " + str(ast))
    else:
        raise Exception("Unknown AST node: " + str(ast))

def generateCondition(ast: Node) -> boolTy:
    global builder
    # Generate the condition and store it in a variable
    builder.append_basic_block("condition")
