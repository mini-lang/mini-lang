from io import StringIO
import unittest

from src.atoms import ValueAtom
from src.evaluator import evaluate
from src.interpreter import globalEnvironment
from src.lexer import Lexer
from src.parser import Parser


def run(source):
    return evaluate(Parser(Lexer(StringIO(source))).parse(), globalEnvironment())


class ControlFlowTests(unittest.TestCase):
    def assert_value(self, source, expected, kind="number"):
        self.assertEqual(run(source), ValueAtom(kind, expected))

    def test_while_updates_outer_counter(self):
        self.assert_value("i = 0 total = 0 while i < 4 { i += 1 total += i } total", 10)
        self.assert_value("i = 0 while (i < 3) i += 1 i", 3)

    def test_conditions_with_unary_calls_and_indexes(self):
        self.assert_value("i = 0 done() = i >= 3 while not done() { i += 1 } i", 3)
        self.assert_value("if not [false][0] { 1 } else { 0 }", 1)
        self.assert_value("negative = [2] result = -negative[0] result", -2)

    def test_empty_and_completed_loops_return_unit(self):
        for source in ["while false { missing }", "for x in [] { missing }",
                       "for x in () { missing }", "for x in [1] { 42 }",
                       "while true { break }", "for x in [1] { break }"]:
            with self.subTest(source=source):
                self.assert_value(source, None, "unit")

    def test_for_iterables_and_inline_body(self):
        cases = [
            ("total = 0 for x in [1, 2, 3] total += x total", 6, "number"),
            ("total = 0 for x in (1, 2, 3) { total += x } total", 6, "number"),
            ("total = 0 for x in 1..4 { total += x } total", 6, "number"),
            ('text = "" for c in "π🌍" { text += c } text', "π🌍", "string"),
            ('text = "" for k in #{a: 1, b: 2} { text += k } text', "ab", "string"),
        ]
        for source, expected, kind in cases:
            with self.subTest(source=source):
                self.assert_value(source, expected, kind)

    def test_iterable_evaluated_once(self):
        self.assert_value("calls = 0 values() = { calls += 1 [1, 2, 3] } for x in values() { x } calls", 1)

    def test_nested_for_break_and_continue(self):
        self.assert_value('''
            total = 0
            for i in 1..4 {
                for j in 1..5 {
                    if j == 2 { continue }
                    if j == 4 { break }
                    total += i * j
                }
            }
            total
        ''', 24)

    def test_nested_while_and_mixed_loops(self):
        self.assert_value('''
            outer = 0 total = 0
            while outer < 3 {
                outer += 1
                inner = 0
                while inner < 5 {
                    inner += 1
                    if inner == 2 { continue }
                    if inner == 4 { break }
                    total += 1
                }
                for x in [1, 2] { total += x break }
            }
            total
        ''', 9)

    def test_for_with_while_break_is_local(self):
        self.assert_value("total = 0 for i in 1..4 { while true { break } total += i } total", 6)

    def test_continue_skips_rest_of_while_body(self):
        self.assert_value("i = 0 total = 0 while i < 6 { i += 1 if i % 2 == 0 continue total += i } total", 9)

    def test_nested_block_assignment_and_local_names(self):
        self.assert_value("x = 1 { { x = x + 2 } } x", 3)
        self.assert_value("x = 1 { { x += 2 } } x", 3)
        self.assert_value("x = y = 4 x + y", 8)
        for source in ["{ local = 1 } local", "for i in [1] { local = 1 } local",
                       "for i in [1] { i } i", "while false { local = 1 } local",
                       "i = 0 while i < 1 { local = 1 i += 1 } local",
                       "for i in [1, 2] { if i == 1 { local = 1 } else { local } }"]:
            with self.subTest(source=source):
                with self.assertRaisesRegex(Exception, "not defined"):
                    run(source)

    def test_for_binding_shadows_without_leaking(self):
        self.assert_value("i = 99 for i in [1, 2] { i += 10 } i", 99)
        self.assert_value("i = 99 for i in [1] { break } i", 99)
        self.assert_value("i = 99 for i in [] { i } i", 99)
        self.assert_value("total = 0 for i in [1, 2] { for i in [8] { i } total += i } total", 3)

    def test_closures_capture_fresh_iteration_bindings(self):
        self.assert_value("fs = [] for i in 1..4 { list_append(fs, () => i) } fs[0]() * 100 + fs[1]() * 10 + fs[2]()", 123)
        self.assert_value("fs = [] i = 0 while i < 3 { n = i list_append(fs, () => n) i += 1 } fs[0]() * 100 + fs[1]() * 10 + fs[2]()", 12)

    def test_parameters_shadow_outer_bindings(self):
        self.assert_value("x = 99 f(x) = { x += 1 x } f(1) + x", 101)
        self.assert_value("x = 99 f = (x) => { x = 2 x } f(1) + x", 101)

    def test_lexical_closure_and_recursion(self):
        self.assert_value("make(x) = () => { x += 1 x } f = make(5) f() f()", 7)
        self.assert_value("factorial(n) = if n <= 1 { 1 } else { n * factorial(n - 1) } factorial(5)", 120)

    def test_return_unwinds_blocks_and_loops(self):
        self.assert_value("f() = { for i in 1..5 { while true { { return i + 10 } } } 99 } f()", 11)
        self.assert_value("f = () => { while true { return 42 } 0 } f()", 42)
        self.assert_value("f() = { return () missing } f()", None, "unit")
        self.assert_value("f() = { if true { return 5 } 99 } f()", 5)

    def test_return_targets_current_function_only(self):
        self.assert_value("f() = { g() = { return 4 } g() 7 } f()", 7)
        self.assert_value("f() = { return 1 } total = 0 for i in 1..4 { total += f() } total", 3)

    def test_loop_inside_function_declared_in_loop(self):
        self.assert_value("total = 0 for i in 1..4 { f() = { for j in [1] { break } 2 } total += f() } total", 6)

    def test_invalid_control_flow_is_rejected_before_evaluation(self):
        for source, keyword in [
            ("break", "break"), ("continue", "continue"), ("return 1", "return"),
            ("{ return 1 }", "return"), ("if false { break }", "break"),
            ("f() = { continue }", "continue"),
            ("while true { f() = { break } break }", "break"),
            ("for i in [1] { f = () => { continue } }", "continue"),
            ("while true { f() = { for j in [] { j } break } break }", "break"),
            ("while break { 1 }", "break"),
        ]:
            with self.subTest(source=source):
                with self.assertRaisesRegex(Exception, keyword + "' is only valid"):
                    Parser(Lexer(StringIO(source))).parse()

    def test_invalid_loop_inputs(self):
        for source, message in [("while 1 { break }", "bool"),
                                ("for x in 3 { x }", "list, tuple, string or map"),
                                ("for x in true { x }", "list, tuple, string or map"),
                                ("for (x, y) in [] { x }", "IDENTIFIER")]:
            with self.subTest(source=source):
                with self.assertRaisesRegex(Exception, message):
                    run(source)

    def test_if_without_else_and_nearest_else(self):
        self.assert_value("if false { missing }", None, "unit")
        self.assert_value("if false { 1 } else if false { 2 } else { 3 }", 3)
        self.assert_value("if true if false 1 else 2", 2)
        self.assert_value("if false { if true 1 } else 3", 3)

    def test_boolean_short_circuit_and_type_check(self):
        self.assert_value("false and missing", False, "bool")
        self.assert_value("true or missing", True, "bool")
        self.assert_value("false && missing", False, "bool")
        self.assert_value("true || missing", True, "bool")
        self.assert_value("n = 0 bump() = { n += 1 true } false and bump() true or bump() n", 0)
        for source in ["1 and true", "false or 1", "true and 1"]:
            with self.subTest(source=source):
                with self.assertRaisesRegex(Exception, "Incompatible types"):
                    run(source)

    def test_tuple_and_unit_remain_single_arguments(self):
        self.assert_value("first(x) = x[0] first((3, 4))", 3)
        self.assert_value("identity(x) = x identity(())", None, "unit")
        self.assert_value("f() = 5 f()", 5)

    def test_invalid_parameters(self):
        for source in ["(1) => 2", "(x, x) => x", "f(x, x) = x", "f(1) = 2"]:
            with self.subTest(source=source):
                with self.assertRaises(Exception):
                    run(source)
