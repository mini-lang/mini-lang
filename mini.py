import sys
from src.interpreter import interpret

# === Global variables ===

USAGE = f"""Welcome to the mini programming language interpreter!
Usage: mini (options) [file.mini]

Options:
    -h, --help      Print this help message and exit
    -r, --repl      Start the REPL
    -d, --debug     Enable debug mode

Examples:
    mini -r         Enter the REPL
    mini file.mini  Evaluate the input file
"""

# === Helper functions ===
def print_error(msg: str):
    print(f"{msg}, try -h or --help to show usage.")
    sys.exit(1)

# === Main ===
def main(args: list):
    debug = False
    if '-d' in args or '--debug' in args:
        debug = True
    if len(args) == 0 or '-h' in args or '--help' in args:
        print(USAGE)
        sys.exit(0)
    elif '-r' in args or '--repl' in args:
        repl(debug)
        sys.exit(0)
    
    # Evaluate
    elif len(args) > 1:
        print_error("Too many arguments")
    elif len(args) == 1:
        interpret(args[-1], debug)
    else:
        print_error("Unknown option")

if __name__ == '__main__':
    # Call main with args
    main(sys.argv[1:])
