#!/usr/bin/env python3
from io import StringIO
import sys
import webbrowser
from src.atoms import ValueAtom
from src.error import MiniError, print_error, print_error_help
from src.colors import BOLD, BRIGHT_YELLOW, GREEN, LOGO, RESET
from src.interpreter import execute, globalEnvironment

# === Global variables ===

USAGE = f"""{BRIGHT_YELLOW}Welcome to the {LOGO} {BRIGHT_YELLOW}interpreter!{RESET}

{BOLD}Usage:{RESET} mini (command) (options) (<file>)

{BOLD}Commands:{RESET}
    repl, r         Start the REPL
    docs, d         Open the documentation
    compile, c      Compile the interpreter to a
                    cross-platform executable binary
    <file>          Interpret the given file

{BOLD}Options:{RESET}
    --help, -h      Print this help message and exit
    --debug, -d     Enable debug mode

{BOLD}Examples:{RESET}
    mini r          Enter the REPL
    mini main.m     Interpret the file main.m
"""

# === Main ===
def main(args: list):
    debug = False
    # Options
    if '--debug' in args or '-d' in args:
        debug = True
        args.remove('--debug') if '--debug' in args else args.remove('-d')
    if len(args) == 0 or '--help' in args or '-h' in args :
        print(USAGE)
        sys.exit(0)
    # Commands
    if 'repl' in args or 'r' in args:
        repl(debug)
        sys.exit(0)
    elif 'docs' in args or 'd' in args:
        webbrowser.open('https://www.mini-lang.org/documentation')
        sys.exit(0)
    elif 'compile' in args or 'c' in args:
        print_error_help("Not implemented yet!")
        sys.exit(0)

    # Interpret file
    if len(args) == 1:
        return interpret(args[-1], debug)
    elif len(args) > 1:
        print_error_help("Too many arguments, expected a single file!")
    else:
        print_error_help("Unknown option")

# Interpreter mode
def interpret(filepath: str, debug = False):
    try:
        with open(filepath, encoding="utf-8") as source:
            execute(source, globalEnvironment(), debug)
        return 0
    except (MiniError, OSError, UnicodeError) as error:
        if debug:
            import traceback
            traceback.print_exc()
        else:
            print_error(error)
        return 1

# Repl mode
def repl(debug = False):
    print(f"{BRIGHT_YELLOW}Welcome to the {LOGO} {BRIGHT_YELLOW}REPL!{RESET}")
    env = globalEnvironment()
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        except KeyboardInterrupt:
            break
        if line == "":
            continue
        try:
            result = execute(StringIO(line), env, debug)
            value, env = result
            if isinstance(value, ValueAtom) and value.type == "unit": continue
            print(value.formatted_str())
        except MiniError as e:
            if debug:
                import traceback
                traceback.print_exc()
            else:
                print_error(e)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
