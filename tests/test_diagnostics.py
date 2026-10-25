from io import StringIO
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from src.error import MiniError
from src.interpreter import execute, globalEnvironment
from src.lexer import Lexer
from tests.test_control_flow import run

ROOT = Path(__file__).resolve().parents[1]


class DiagnosticTests(unittest.TestCase):
    def error(self, source):
        stream = StringIO(source)
        stream.name = "sample.m"
        with self.assertRaises(MiniError) as caught:
            execute(stream, globalEnvironment())
        self.assertEqual(caught.exception.source, "sample.m")
        return caught.exception

    def test_token_starts_and_eof(self):
        lexer = Lexer(StringIO('  alpha\n\t"π" += 12..14'))
        tokens = [lexer.next_token() for _ in range(7)]
        self.assertEqual([(t.name, t.line, t.column) for t in tokens], [
            ("IDENTIFIER", 1, 3), ("STRING", 2, 2), ("PLUSEQUAL", 2, 6),
            ("NUMBER", 2, 9), ("RANGE", 2, 11), ("NUMBER", 2, 13), ("EOF", 2, 15),
        ])

    def test_lexical_errors(self):
        for source, line, column, message in [
            ("\n  @", 2, 3, "Unexpected character"),
            ("1\0missing", 1, 2, "Unexpected character"),
            ("²", 1, 1, "Invalid number literal"),
            ('\n  "unterminated', 2, 3, "Unterminated string"),
            ("\n /* unterminated", 2, 2, "Unterminated block comment"),
            ('"bad\\q"', 1, 1, "Invalid escape sequence"),
        ]:
            with self.subTest(source=source):
                error = self.error(source)
                self.assertEqual((error.kind, error.line, error.column), ("Lexical", line, column))
                self.assertIn(message, error.message)

    def test_syntax_errors(self):
        for source, line, column, message in [
            ("\n  break", 2, 3, "only valid inside a loop"),
            ("\n  return 1", 2, 3, "only valid inside a function"),
            ("if true {\n", 2, 1, "Expected RBRACE"),
            ("[1, 2", 1, 6, "RBRACKET"),
            ("(1, 2", 1, 6, "RPAREN"),
            ("f() = { return }", 1, 9, "Return requires a value"),
            ("(x, x) => x", 1, 5, "Duplicate parameter"),
            ("(1) => 2", 1, 2, "parameter must be an identifier"),
            ("if true: 1", 1, 8, "Colon bodies"),
        ]:
            with self.subTest(source=source):
                error = self.error(source)
                self.assertEqual((error.kind, error.line, error.column), ("Syntax", line, column))
                self.assertIn(message, error.message)

    def test_runtime_errors_use_innermost_location(self):
        for source, line, column, message in [
            ("x = 1\n  missing", 2, 3, "not defined"),
            ("x = 1\n x / 0", 2, 4, "division by zero"),
            ('f() = {\n  missing\n}\nf()', 2, 3, "not defined"),
            ('f(x) = x\nf()', 2, 2, "expects 1 arguments"),
            ('while true {\n  if 1 { break }\n}', 2, 6, "Condition must evaluate to a bool"),
            ('\nfor x in 3 { x }', 2, 1, "For loop expects"),
            ('\n[1][3]', 2, 4, "index 3 is out of range"),
            ('\nassert(false)', 2, 7, "Assertion failed"),
        ]:
            with self.subTest(source=source):
                error = self.error(source)
                self.assertEqual((error.kind, error.line, error.column), ("Runtime", line, column))
                self.assertIn(message, error.message)

    def test_deferred_constructs_are_explicit_errors(self):
        for source in ["class Animal {}", "enum Option {}", "match 1", "1 is number",
                       "1 in [1]", "import module", "none", "true & false", "true | false",
                       "~1", "x = 1 x *= 2", "1..", "for i in 1.. { i }",
                       "for (k, v) in #{} { k }", "[1].append(2)", "1; 2"]:
            with self.subTest(source=source):
                self.assertIn("not supported in v1", self.error(source).message)

    def test_long_whitespace_and_comments_at_eof(self):
        self.assertEqual(run(" " * 5000 + "1").value, 1)
        self.assertEqual(run("1 // no trailing newline").value, 1)
        self.assertEqual(run("/*comment*/" * 2000 + "2").value, 2)
        self.assertEqual(run("// only a comment").type, "unit")

    def test_ranges_and_computed_collection_assignment(self):
        self.assertEqual([x.value for x in run("123..126").value], [123, 124, 125])
        self.assertEqual(run("items = [1, 2] for i in 0..2 { items[i] = items[i] + 10 } items[1]").value, 12)
        self.assertEqual(run('m = #{a: [1]} k = "a" m[k][0] = 7 m.a[0]').value, 7)
        self.assertEqual(run('m = #{} k = "new" m[k] = 3 m.new').value, 3)
        self.assertEqual(run('m = #{1: 3} m[1]').value, 3)
        self.assertEqual(run("#{false: 7}[false]").value, 7)
        for source, message in [("1.5..4", "Range bound must be an integer"),
                                ("[1][0.5]", "Index must be an integer"),
                                ("[1][0:1:0]", "Slice step must not be zero"),
                                ("[1][0:1.5]", "Slice end must be an integer"),
                                ("#{a: 1}['missing']", "Map does not contain key"),
                                ("x = (1, 2) x[0] = 3", "Only lists and maps"),
                                ("x = [1] x[0:1] = [2]", "Slice assignment is not supported")]:
            with self.subTest(source=source):
                self.assertIn(message, self.error(source).message)


class CLITests(unittest.TestCase):
    def invoke(self, source, *options):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "program.m"
            path.write_text(source, encoding="utf-8")
            return subprocess.run([sys.executable, str(ROOT / "mini.py"), *options, str(path)],
                                  capture_output=True, text=True, encoding="utf-8", timeout=5)

    def test_program_errors_have_nonzero_status_and_stderr(self):
        for source in ['@', 'if true {', 'break', 'class X {}', '1 / 0', 'missing',
                       'print("should not execute") continue']:
            with self.subTest(source=source):
                result = self.invoke(source)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertRegex(result.stderr, r"program\.m:\d+:\d+: (Lexical|Syntax|Runtime) error:")
                self.assertNotIn("Traceback", result.stderr)

    def test_success_empty_input_and_error_word(self):
        for source, output in [('', ''), ('// eof', ''), ('print("error 🌍")', 'error 🌍\n')]:
            with self.subTest(source=source):
                result = self.invoke(source)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, '')
                self.assertEqual(result.stdout, output)

    def test_debug_errors_still_fail(self):
        result = self.invoke('missing', '--debug')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('program.m:1:1: Runtime error:', result.stderr)

    def test_missing_file_fails_cleanly(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(ROOT / 'mini.py'), str(Path(directory) / 'absent.m')],
                                    capture_output=True, text=True, timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('absent.m', result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_repl_recovers_and_exits_on_eof(self):
        result = subprocess.run([sys.executable, str(ROOT / 'mini.py'), 'repl'],
                                input='x = 41\nmissing\nx + 1\n',
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0)
        self.assertIn('42', result.stdout)
        self.assertIn('<input>:1:1: Runtime error:', result.stderr)
