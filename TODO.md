# Todo list
The language design and future ideas below remain part of Mini's direction.
The [v1 guide](docs/v1-guide.md) and [capability matrix](docs/v1.md) describe current
implementation support; deferring a feature from v1 does not remove it from the design.

## Educational v1 progress

- [x] Record supported syntax and run v1 guide examples automatically.
- [x] Exercise every example file, including Unicode and scripted input.
- [x] Add `while`, `for`, scoped iteration variables, `break` and `continue` (#6).
- [x] Add function-only `return` and reject invalid control flow (#6).
- [x] Define assignment to enclosing scopes; preserve local parameters.
- [x] Fix chained `else if`, false `if` without `else`, and short-circuit logic.
- [x] Preserve tuple/unit call arguments; validate function parameters.
- [x] Report lexical, syntax and runtime errors with source locations.
- [x] Return nonzero CLI status on program errors; keep the REPL usable after errors.
- [x] Align the companion website/tutorial with verified v1 behavior.

## Language design backlog

Some items have partial implementations already, especially in the experimental
standard library. Their presence here retains the broader design and improvement
work; consult the capability matrix for the verified subset.

- [x] Setting values on hash map objects.\
	Example: `map[key] = value`
- [ ] Propper error handling. Pretty printed errors with detailed information about the error location, type, and message. Take inspiration from other languages.
	V1 now reports source, line, column, kind and message; richer presentation remains future work.
- [ ] Function variations, variables that are assigned lambdas should have support for overloading with different signatures. Correct function should be found using pattern matching on the argument list or simply matching by the number of arguments passed to the function.
- [x] Implementing the `for` loop.
- [x] Implementing the `while` loop.
- [ ] Implementing pattern matching with support for complex patterns.\
	Examples:
	- `if mystr is "hello" + rest` Checks if `mystr` starts with `hello` and then binds `rest` to the rest of the string if the pattern matches.
	- `if num is number(n)` Checks if `num` is a number and then binds `n` to the number if the pattern matches.
	- `if mymap is #{a: 1, b: c}` Checks if `mymap` is a hash map with keys `a` and `b` where the value of `a` is `1`, then binds `c` to the value of `b` if the pattern matches.
	- `(a, b) = (1, 2)` Binds `a` to `1` and `b` to `2`.
	- `(c, d, e) = tuple` Binds the tuple elements to `c`, `d` and `e` if it has the same number of elements.
	- `[f, s | t] = [1, 2, 3, 4]` Binds `f` to `1`, `s` to `2`, and `t` to `[3, 4]`.
- [ ] Implementing the `match` statement.
- [ ] Implement enum types.
- [ ] Implement atom types. (Atom types are types that can only be created once and cannot be changed.)\
	Example: `atm = :hello_world` then `atm == :hello_world` is always true.
- [ ] Unicode support for identifiers and atoms. (Strings already support unicode encodings)
	V1 supports Unicode letters in identifiers; atom literals and broader identifier syntax remain future work.
- [ ] More escape sequences for strings.
- [ ] Expand standard library.
	- [ ] Filesystem, open files and read/write contents.
	- [ ] Networking.
	- [ ] Time and date.
	- [ ] Random numbers.
	- [ ] Regular expressions.
	- [ ] String formatting. `format("a={} b={}", a, b)` or similar.\
		Is this a good idea to feature in the base language?
	- [ ] Math, trigonometry, and other functions.
	- [ ] Encoding/decoding.
	- [ ] Encryption/decryption.
	- [ ] Compression/decompression.
	- [ ] Serialization/deserialization.
	- [ ] Parse different file formats, like JSON, XML, YAML, etc.
	- [ ] Console input/output with color and formatting support. (ANSI escape codes, etc.)
	- [ ] More data structures such as linked lists, stacks, queues, sets, trees, hash tables, binary trees, and graphs.
	- [ ] More algorithms such as sorting, searching, and hashing.
	- [ ] Type casting functions for converting between types. `number("1.5")`, `string([])` or similar.
- [ ] Implementing the `import` statement with support for relative paths.
- [ ] Module system with import and export keywords.
- [ ] Bootstrapping the language and writing a native compiler for it.
- [ ] Implementing classes with support for inheritance, polymorphism and static methods.


### Future development

- [ ] Type system, incremental type checking, and type inference, or static typing.
- [ ] Range indexing for lists and strings\
	Examples:
	- `list[0:2]` returns the first two elements of the list.
	- `list[:-1]` returns the list without the last element.
	- `list[1:]` returns the list without the first element.

### Third-party tools
This might be a good place to look if you are interested in contributing to the language ecosystem!

- [ ] Documentation generator that parses the source code and generates documentation in markdown format or for the web.
- [ ] Compiler for the language that compiles the source code to native machine code, LLVM, or for the web.
