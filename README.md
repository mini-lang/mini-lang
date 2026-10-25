<div align="center">
    <img alt="Mini-Lang logo" src="assets/logo_small.png" width="350px"/>
</div>

# The `mini` language

`mini` is a small, dynamically typed, expression-based language for learning
interpreter design, built for [Write a language in a week](https://dev.to/williamragstad/series/17603).
The educational v1 subset is described below; it is not the full language proposed
in earlier documentation.

## Run it

Python **3.10 or later** is required. The interpreter has no third-party dependencies.

```sh
git clone https://github.com/mini-lang/mini-lang
cd mini-lang
python mini.py examples/hello_world.m
python mini.py repl
python test.py
```

## Active implementation

`mini.py` → `src/interpreter.py` → `src/parser.py` / `src/lexer.py` →
`src/manual/` → `src/evaluator.py`.
The public parser, lexer and AST modules re-export the handwritten implementation.
[`src/grammar/mini.lark`](src/grammar/mini.lark) is an **experimental design draft**;
it is not loaded by the CLI and accepting syntax there does not implement it.
See the [capability matrix](docs/v1.md) for differences and the [TODO](TODO.md) for
work outside v1.

## Executable v1 examples

Every `mini` code fence in this README and `docs/` is executed by `python test.py`
in a fresh environment. `// =>` lines specify exact printed output. All files in
[`examples/`](examples/) are also exercised, including scripted input.

### Values, operators and variables

Numbers, booleans, strings, lists, tuples, maps and unit `()` are supported.
Use `+ - * / % ^`, comparisons, and `and` / `or` / `not` (also `&&` / `||` / `!`).
Single `&` and `|` are not boolean operators. Assignments create variables.
Names may contain Unicode letters, digits after the first letter, and underscores;
emoji identifiers are not supported. Underscore-prefixed names are ordinary variables.

```mini
x = 10
y = 2 * x + 1
_ordinary = "hello"
print(y, _ordinary, not false)
// => 21 hello true
```

Whitespace separates expressions; newlines are whitespace, not statement terminators.
There are no semicolons. Write calls and indexes adjacent to their receiver, as in
`f(x)` and `items[0]`. Use braces for control-flow bodies to avoid ambiguous inline
expressions. Comments use `//` or `/* ... */`.

### Blocks and functions

A block evaluates to its last expression; an empty block evaluates to `()`.
New names inside a block stay local. Functions capture their defining environment,
accept fixed positional parameters, and return their body's value.

```mini
answer = {
    local = 21
    local * 2
}
add(x, y) = x + y
square = (x) => x * x
print(answer, add(1, 2), square(4))
// => 42 3 16
```

### Collections and built-ins

Use free functions such as `list_append(items, value)`, `list_size(items)`,
`list_map(items, fn)` and `map_size(m)`, not methods such as `items.append(value)`.
The conversion names are `str`, `number`, `int` and `bool` (not `string`).
`print`, `input`, `typeof` and `assert(condition, message)` are also available.
The larger host-oriented library in `src/stdlib.py` remains experimental.

```mini
items = [1, 2, 3]
list_append(items, 4)
print(list_map(items, (x) => x * 2))
print(items[-1], items[1:3])
m = #{name: "Ada"}
m.name = "Mini"
print(m.name, map_size(m), str(true))
print("tuple:", (1, 2) + (3, 4))
// => [2, 4, 6, 8]
// => 4 [2, 3]
// => Mini 1 true
// => tuple: (4, 6)
```

Ranges are **eager, ascending, end-exclusive integer lists**, like Python's
`range`: `1..4` contains 1, 2 and 3. Both bounds are required. Slices also exclude
the end and currently require both start and end (`items[1:3:2]`). Maps store
string keys, including the string form of numeric and boolean literal keys.
`(x)` groups an expression, `(x, y)` is a tuple, and `()` is unit.

```mini
print(1..4)
print(4..1)
// => [1, 2, 3]
// => []
```

### Control flow

`if` is an expression with a boolean condition and optional `else`.

```mini
x = 7
label = if x >= 5 { "medium" } else { "small" }
print(label)
// => medium
```

`while`, `for`, `break`, `continue` and function-only `return` are the remaining
v1 work in the next change; see [the subset contract](docs/v1.md).

## Development

Run `python test.py` for legacy tests, executable examples and the standard-library
`unittest` suite. New tests go in `tests/test_*.py` and are discovered automatically.
See [CONTRIBUTING.md](CONTRIBUTING.md). The companion website and tutorial live in
[mini-lang.github.io](https://github.com/mini-lang/mini-lang.github.io).

Classes, enums, pattern matching, sets, modules, open-ended ranges and a Lark
runtime are deferred. Do not infer their availability from the grammar draft.

## License

[MIT](LICENSE). Contributions and experiments with the language are welcome.
