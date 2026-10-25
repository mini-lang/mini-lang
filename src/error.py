import sys

from .colors import RED, RESET


class MiniError(Exception):
    """A language error with a one-based source location."""
    def __init__(self, kind: str, message: str, location=None):
        super().__init__(message)
        self.kind = kind
        self.message = message
        self.source = getattr(location, "source", "<input>")
        self.line = getattr(location, "line", 1)
        self.column = getattr(location, "column", 1)

    def __str__(self):
        return f"{self.source}:{self.line}:{self.column}: {self.kind} error: {self.message}"


def print_error(error):
    message = str(error) if isinstance(error, MiniError) else f"Error: {error}"
    if sys.stderr.isatty():
        message = f"{RED}{message}{RESET}"
    print(message, file=sys.stderr)


def print_error_help(msg: str, exit=True):
    print_error(msg)
    print("\nTry -h or --help to show usage.", file=sys.stderr)
    if exit:
        sys.exit(1)
