# TODO

The [v1 capability matrix](docs/v1.md) distinguishes the active handwritten
interpreter from the experimental Lark grammar. Grammar productions alone do not
count as implemented features.

## Educational v1

- [x] Record supported syntax and run README examples automatically.
- [x] Exercise every example file, including Unicode and scripted input.
- [x] Add `while`, `for`, scoped iteration variables, `break` and `continue` (#6).
- [x] Add function-only `return` and reject invalid control flow (#6).
- [x] Define assignment to enclosing scopes; preserve local parameters.
- [x] Fix chained `else if`, false `if` without `else`, and short-circuit logic.
- [x] Preserve tuple/unit call arguments; validate function parameters.
- [ ] Report lexical, syntax and runtime errors with source locations.
- [ ] Return nonzero CLI status on program errors; keep the REPL usable after errors.
- [ ] Align the companion website/tutorial with verified v1 behavior.

## Deferred beyond v1

- Classes, inheritance, enums, atom literals, sets and pattern matching (`match`,
  `is`, destructuring, pattern parameters and for bindings).
- Membership `in` outside a for header; additional compound/bitwise operators.
- Open-ended/lazy ranges and slices with omitted bounds.
- Function overloading, imports/modules, a type system and native compilation.
- Adopt a Lark runtime only with an explicit syntax migration and parity tests.
- Expand and validate the experimental host library (filesystem, networking,
  encoding, random, time and additional collection helpers already exist).
- Documentation generators, tooling and other interpreter backends.
