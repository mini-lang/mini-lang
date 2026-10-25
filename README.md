<div align="center">
    <br>
    <img alt="Mini-Lang logo" src="assets/logo_small.png" width="350px"/>
    <p>
    <br>
        <b>The mini programming language</b> built for the<br>
        <a href="https://dev.to/williamragstad/series/17603" about="_blank">
            <em>Write a language in a week</em>
        </a> series.
    </p>
    <br>
</div>

# The `mini` language

> **Language design and current implementation**
> The specification below describes the intended Mini language, including features
> that are still planned. It remains the project's design direction.
> For what runs today, see the [educational v1 guide](docs/v1-guide.md) and
> [capability matrix](docs/v1.md). The CLI uses the handwritten parser in
> `src/manual/`; the Lark grammar is a separate syntax design draft.
> The v1 guide's `mini` examples are tested automatically. The design examples
> below illustrate intended behavior and are not all executable in v1.

This is the repository for the example programming language `mini` built for the [*Write a language in a week*](https://dev.to/williamragstad/series/17603) series. Read the full series.

`mini` is a minimal programming language that is built for the purpose of teaching programming language design.
The language is dynamically typed and expression-based. It is designed to be easy to learn and use. The intended design supports both functional and object oriented programming paradigms.

It is not intended to be a full language, but rather a language that can be expanded upon and explore new and more advanced concepts in language design.


<br/>
<!-- Start Document Outline -->

## Table of contents

- [Table of contents](#table-of-contents)
- [Installation](#installation)
  * [Persistent installation](#persistent-installation)
- [Features](#features)
- [Specification](#specification)
  * [Primitive data types](#primitive-data-types)
  * [Variable declaration](#variable-declaration)
  * [Comments](#comments)
  * [Lambda expressions](#lambda-expressions)
  * [Functions](#functions)
  * [Collection data structures](#collection-data-structures)
    + [More on collection data structures](#more-on-collection-data-structures)
  * [Enums](#enums)
  * [Classes](#classes)
  * [Built-in functions](#built-in-functions)
  * [Control flow structures](#control-flow-structures)
  * [Other keywords and operators](#other-keywords-and-operators)
- [Contribute! 🎉](#contribute-)
  1. [Perfecting the language 👑](#1-perfecting-the-language-)
  2. [Improve the documentation 📝](#2-improve-the-documentation-)
  3. [Expand the ecosystem 🏕️](#3-expand-the-ecosystem-%EF%B8%8F)
  4. [Get involved in the community 🫂](#4-get-involved-in-the-community-)
  5. [Improve the article series 📚](#5-improve-the-article-series-)
- [License](#license)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>

<!-- End  Document Outline -->
<br/>

## Installation

Install the latest version of `mini` using the commands below.

```bash
> git clone https://github.com/WilliamRagstad/mini-lang
> cd mini-lang
> py mini.py
```

The `mini` interpreter is written in [Python](https://www.python.org/) and requires version **3.10 or later**, with no third-party Python dependencies.

### Persistent installation

1. Clone the repository to a program directory of your choice.
Suggested directory: `C:\Program Files`, `C:\Program Filed (x86)` or `/usr/local/bin`.

2. Add the directory to your `PATH` environment variable. E.g. `/usr/local/bin/mini-lang`.

3. Done! Run the `mini` interpreter from any directory.

## Features

The intended language design includes:

* Basic arithmetic, logic, and comparison operators
* Primitive data types such as `number`, `bool`, and `string`
* Collection data structures like `list`, `tuple`, `map`, and `set`
* Lambda expressions and functions
* Classes and inheritance
* Enum types
* Variables
* Code blocks
* C-stlye Comments
* A set of built-in functions
* Basic control flow structures
* Other keywords and operators

## Specification

This is the intended language design. Consult the [v1 capability matrix](docs/v1.md)
for implemented features and current differences in syntax and behavior.

The syntax of `mini` is similar to the [ECMAScript specification](https://tc39.es/ecma262/), but not identical.

### Primitive data types

There are three primitive data types in `mini`:
* `number` - Represents both floating point and integer numbers
    * Arithmetic operators: `+`, `-`, `*`, `/`, `%` (modulo)
    * Comparison operators: `==`, `!=`, `<`, `<=`, `>`, `>=`
    * Examples: `21`, `4.2`, `-3`, `-3.5`
* `bool` - Represents logical `true` or `false`
    * Logical operators: `&` (and), `|` (or), `!` (not)
    * Comparison operators: `==`
    * Examples: `true`, `false`
* `string` - Represents a sequence of characters, or a single character
    * Arithmetic operators: `+` (concatenation)
    * Comparison operators: `==`, `!=`
    * Examples: `"hello"`, `'world'`, `"a"`, `'b'`


### Variable declaration
A variable declaration is the same as an assignment, but if the variable is not already declared, it is automatically declared.

```js
x = 10
```

Multiple variables can be declared with the same value in a single statement.

```js
x = y = z = 10
```

Or multiple variables can be declared with different values on a single line, must be separated by whitespace.

```js
x = 10  y = 20  z = 30
```

All variable identifiers **starting** with an underscore `_` are treated as "don't care" variables. Meaning its value is "thrown away" when bound in a scope.

```ts
_ignored = 10
print(_ignored) // Error, _ignored is not defined
```

This is useful for catching all values in a pattern match.

```fs
match x
    | 10 -> "ten"
    | _ -> "other" // Catch all values not already matched
```

Variables can also be set to the return value of a code block.

```js
x = {
	y = 10
	y * 2
}
x // 20
```

### Comments

```ts
// Single-line comment
/* Multi-line
   comment */
```

There are also unofficial block comment syntax for documentation.
This is not currently supported in this language, but mainly processed by documentation tools to generate application programming interface (API) documentation.

```ts
/**
 * Documentation comment
 *
 * @param {number} x
 * @param {string} y
 * @returns {bool}
 **/
```

### Lambda expressions

Lambdas are declared with the `=>` operator.
The left hand side of the `=>` is the parameter-list tuple, and the right hand side is the function body (A single expression or block).

```js
(x, y) => x + y
```

Empty parameter-list lambdas can be declared with an empty tuple. Used for generator and supplier functions.

```js
() => 42
```

### Functions

A function is simply a lambda expression bound to a variable.
Functions can be declared by assigning a lambda expression to a variable as seen below.

```cs
add = (x, y) => x + y
add(1, 2)
```

Alternative syntax sugar for functions is to directly specify the parameter-list and function body separated by an assignment operator.

```cs
add(x, y) = x + y
```

These two forms are equivalent as the latter is a shorthand for the former.

Functions can also have a body block.

```cs
add(x, y) = {
    z = y * 2
    x + z // Return value
}
```

`mini` has therefore **higher-order functions**.
As functions and lambdas are the same thing, they can be used interchangeably. The value of a function is the value of the lambda expression.

```cs
add = (x, y) => x + y // Lambda expression style
add10(y) = add(10, y) // Function style
[1, 2, 3].map(add10)  // Function passed as parameter
// [11, 12, 13]
```

### Collection data structures

Primitive data types are useful, but limiting on their own. `mini` has a number of data structures that can be used to store and manipulate collections of data.
* `list` - An ordered collection of values, where each value can be accessed by index. Elements are stored in the order they are declared.
    * Examples:
        * `[1, 2, 3]` - A list of three integers
        * `[true, false, 'hello', 'world']` - Mixed types
        * `[]` - An empty list
		* `list[0]` - Access the first element
		* `list[-1]` - Access the last element
		* `list[5] = 10` - Set the sixth element to 10
	* Operators:
		* `list1 + list2` - Concatenate two lists
		* `list[index]` - Access an element by index (zero-based)
    * Methods:
        * `list.length` - The number of values in the list
        * `list.append(value)` - Adds a value to the end of the list
        * `list.prepend(value)` - Adds a value to the beginning of the list
        * `list.pop()` - Removes and returns the last value in the list
        * `list.shift()` - Removes and returns the first value in the list
        * `list.map(fn)` - Returns a new list with the values transformed by the given function
        * `list.filter(fn)` - Returns a new list with the values filtered by the given function
        * `list.reduce(fn, initialValue)` - Returns a single value by combining the values in the list
        * `list.indexOf(value)` - Returns the index of the given value, or `-1` if the value is not in the list
        * `list.lastIndexOf(value)` - Returns the index of the last given value, or `-1` if the value is not in the list
        * `list.join(separator)` - Returns a string with the values in the list separated by the given separator
* `tuple` - An ordered collection of values, where each value can be accessed by index.
    * Examples:
        * `(1, 2, 3)` - A tuple of three integers
        * `('hello', 'world')` - A tuple of two strings
        * `()` - An empty tuple, or `unit`. **This should be treated the same as `null` in other languages.**
	* Operators:
		* `tuple1 + tuple2` - Add the values of two tuples together (element-wise).
        * `tuple[index]` - The value at the given index
    * Methods:
        * `tuple.length` - The number of values in the tuple
* `map` - A disorderly collection of hashed key-value pairs, where each key can be accessed by index.
    * Examples:
        * `#{a: 1, b: 2, c: 3}` - A map of three key-value pairs
        * `#{0: 1, 1: 2, 2: 3}` - A map with numeric keys
        * `#{'hello world': 'hello', 'goodbye world': 'goodbye'}` - A map with string keys
        * `#{}` - An empty map
		* `map['test'] = 123` - Assigns a value to the given key
	* Operators:
		* `map1 + map2` - Concatenate two maps together (merge the values of the two maps).
		* `map[key]` - The value at the given key
    * Methods:
        * `map.<key>` - The value associated with the given key, ie. `map.abc` is equivalent to `map['abc']`
        * `map.has(key)` - Returns `true` if the map contains the given key
        * `map.delete(key)` - Removes the value associated with the given key
        * `map.clear()` - Removes all key-value pairs from the map
        * `map.keys()` - Returns a new list with the keys in the map
        * `map.values()` - Returns a new list with the values in the map
        * `map.entries()` - Returns a new list with the key-value pairs in the map

#### More on collection data structures

There are many tips and tricks for working with collections.
For example, it is possible to use a list as a stack.

```ts
stack = [1, 2, 3]
stack.append(4)
print(stack) // [1, 2, 3, 4]
stack.pop()
print(stack.pop()) // 3
```

It is also possible to use a list as a queue.

```ts
queue = [1, 2, 3]
queue.append(4)
print(queue) // [1, 2, 3, 4]
queue.shift()
print(queue.shift()) // 2
```

Or even a reversed queue.

```ts
queue = [3, 2, 1]
queue.prepend(4)
print(queue) // [4, 3, 2, 1]
queue.pop()
print(queue.pop()) // 2
```

Lists have support for partial pattern matching, utilizing the `|` operator to separate elements from the rest of the list in a pattern match.
You can extract values from different collections using pattern matching as shown below.

```fs
match [1, 2, 3]
    | [f, s | t] => print(f, s, t) // 1 2 [3]
    | [h | t] => print(h) // 1
    | [] => print('empty list') // empty list
    | _ => print('other') // other type
```

```cs
list = [1, 2, 3]
if list is [head | tail] {
    print(head) // 1
    print(tail) // [2, 3]
}
```

Maps have also support for partial pattern matching.

```fs
match #{a: 1, b: 2, c: 3}
    | #{a: f, b: s} => print(f, s) // 1 2
    | #{a: f} => print(f) // 1
    | #{} => print('empty map') // empty map
    | _ => print('other') // other type
```

> A **Set** is a collection of unique values.\
> `mini` provides a `set` data structure in its standard library for storing and manipulating unique values in an unordered collection.

Examples:
* `set(1, 2, 3)` - Initialize a set with three unique values.
* `set()` - The empty set.

Methods:
* `set.length` - The number of values in the set
* `set.has(value)` - Returns `true` if the set contains the given value
* `set.add(value)` - Adds the given value to the set
* `set.delete(value)` - Removes the given value from the set
* `set.clear()` - Removes all values from the set
* `set.values()` - Returns a new list with the values in the set


### Enums

`mini` supports Rust-like enums.

```fs
enum Optional {
    Some(value),
    None
}

x = Optional.Some(42)
y = Optional.None
z = Optional.Some([1, 2, 3])
```

All identifiers in an enum value argument list must be unique. The values are assigned to the identifiers in the order they are declared and are dynamically typed.

### Classes

```ts
Animal = class {
    Animal(name) = #{
        name: name
    }

    speak() = {
        return "{this.name} makes a noise."
    }
}
```

In the example above, `Animal` is a class with a constructor and a `speak` method.
The method is defined as a function expression, which has an implicit `this` parameter.

`mini` also supports basic inheritance.

```ts
Dog = class : Animal {
    Dog(name) = {
        // Code block with logic other than just a map
        return #{
            name: name,
            dogSpecificSound: "Woof"
        }
    }

    speak() {
        return "{this.speak()} {this.dogSpecificSound}!"
    }
}
```

Running this with the code below will produce the following output:

```ts
dog = Dog("Fido")
dog.speak() // "Fido makes a noise. Woof!"
```

Classes are instantiated simliar to function calls, other languages like Python have a similar syntax.

```ts
animal = Animal("Pig")
animal.speak() // "Pig makes a noise."
animal.name // Ok, returns "Pig"
animal.dogSpecificSound // Throws an error, since dogSpecificSound is not defined on Animal
```

Because classes also are expressions, they can be assigned to variables. This is useful for creating objects that are used in multiple places, or for creating objects that are passed to functions.
This is also how static methods can be defined on a class.

```ts
MyClass = class {
    hello() {
        return "Hello world!"
    }
}
MyClass.hello()     // Throw an error, since hello is only defined on MyClass instances
MyClass.bye()       // Throws an error, since bye is not defined on MyClass
myInstance = MyClass()
myInstance.hello()  // "Hello world!"
myInstance.bye()    // Throws an error, since bye is not defined on MyClass instances
// Define a static method on MyClass
MyClass.bye = () => {
    return "Bye world!"
}
MyClass.bye()       // "Bye world!"
myInstance.bye()    // Throws an error, since bye is not defined on MyClass instances byt on MyClass itself
```
> Note: `mini` does not support static methods inside of class expressions.\
> Instead, static methods can be defined on the class value itself as shown above for `MyClass.bye`.


### Built-in functions

There are a number of built-in functions that can be used in `mini`:
* `print` - Prints a string to the console
    * Examples:
        * `print('hello')`
        * `print("hello", "world")`
        * `print(1, 2, 3)`
* `input` - Gets a string from the console
    * Examples:
        * `input()`
        * `input("Enter your name: ")`

There are also a number of helper functions to convert values between different types.
* `string` - String representation of a given value
    * Examples:
        * `string([1, 2, 3])`
        * `string(1.23)`
        * `string(true)`
        * `string(#{'a': 1, 'b': 2})`
        * `string("hello")`
* `number` - Integer representation of a given value
    * Examples:
        * `number('1')`
        * `number(1.23)`
        * `number(true)` - Returns `1`
        * `number(#{'a': 1, 'b': 2})` - Fails with an error
        * `number("hello")` - Fails with an error
* `bool` - bool representation of a given value
    * Examples:
        * `bool('1')` - Returns `true`
        * `bool(1.23)` - Returns `true`
        * `bool(0)` - Returns `false`
        * `bool(true)` - Returns `true`
        * `bool("")` - Returns `false`
        * `bool(#{'a': 1, 'b': 2})` - Returns `true`
        * `bool("hello")` - Returns `true`

### Control flow structures

There are three control flow structures in `mini`:
* `if` - If-then-else statement
* `match` - Pattern matching statement
* `for` - For-loop
* `while` - While-loop
* `break` - Break out of a loop
* `continue` - Continue to the next iteration of a loop
* `return` - Return from a function, last expression in a block is implicitly returned

Below are examples of each control flow structure.

> **`if` statement**
>
> The `if` statement is used to execute and return the value of a block of code or a single expression if a condition guard is true.

The guard is an expression directly following the `if` keyword, surrounding parentheses are optional. After that, a block of code or a single expression is specified.

```js
if x == 1 "one"
```

The example above returns the string `"one"` if the condition `x == 1` is true.

```js
if x % 2 == 0 {
    x *= 2
    return x + 1
}
```

The example above returns the value of `x * 2 + 1` if `x` is even.

If statements also has the power to pattern match on values using the `is` operator.

> **`if-else` statement**
>
> The `if-else` statement is used to execute and return the value of different blocks of code or single expressions depending on the value of a condition guard.

The code below is a short implementation of the absolute value function `|x|`.

```js
if x > 0 x
else -x
```

> **`else if` statement**
>
> The `else if` statements can be used to add additional conditions to an `if-else` statement.

```fs
if x >= 10 "ten or more"
else if x >= 5 "five or more"
else if x >= 1 "one or more"
else "none"
```

> **`match` statement**
>
> The `match` statement matches a value against a set of patterns, and returns the value of the first pattern that matches.

First specify the value to match against, then specify a list of patterns separated by `|` characters.
The first pattern that matches the value is the one that gets evaluated and returned.

```fs
match x
    | 1 => "one"
    | 2 => "two"
    | _ => "many"
```

One could think of match as many `if x is p` statements combined into a single statement.

A match case can also have a guard using the `if` keyword, which ensures that the pattern on the left hand side also satesfies a logical condition on the right hand side, before evaluating the matching case expression.

```fs
match x
    | number(n) if n > 0 => "positive"
    | number(n) if n < 0 => "negative"
    | number(n) if n == 0 => "zero"
    | _ => "not a number"
```

You can also inline the pattern list, which is useful when the pattern list is short.

```fs
x = Optional.Some(1)
match x | Some(n) => "some" | None => "none"
```

> **`for` statement**
>
> The `for` statement is used to iterate over a list of values or an iterator.

The syntax is similar to the `for` loop in other languages such as Python and Ruby, using the `in` keyword to specify the list or iterable.

```fs
for x in [1, 2, 3] print(x)
```

Using a lazy iterator is possible by using the `..` operator.

```fs
for x in 1..10 print(x)
```

It is also possible to iterate over a map where the keys are used as the iterator. This is because the map data structure implements the `Iterator` class interface.

```ts
m = #{a: 1, 'b': 2, "c": 3}
for x in m
    print(x)
// prints a, b, c
```

Passing an extra pattern argument, `v` for example, to the `for` statement is used to specify a variable to be used as the iterator value.
In this case the variable `k` is the key and `v` is used to store the value of each map entry.

```ts
m = #{a: 1, 'b': 2, "c": 3}
for (k, v) in m
    print(k, v)
// prints a 1, b 2, c 3
```

> **`while` statement**
>
> The `while` statement is used to execute a block of code while a condition is true.

The guard is an expression directly following the `while` keyword, surrounding parentheses are optional. After that, a block of code or a single expression is specified.

```ts
while x < 10 x += 1
```

Alternative styles of writing a while loop are also possible.

```ts
while x < 10 {
    x += 1
}
```

```ts
while (x < 10) x += 1
```

Or both.

```ts
while (x < 10) {
    x += 1
}
```

> **`break` statement**
>
> The `break` statement is used to break out of the nearest enclosing loop.

```ts
while x < 10 {
    x += 1
    if x == 5 break
}
```


> **`continue` statement**
>
> The `continue` statement is used to continue to the next iteration of the nearest enclosing loop.

```ts
while x < 10 {
    x += 1
    if x % 2 == 0 continue
    print(x)
}
```
The example above prints all odd numbers from 1 to 10. E.g. 1, 3, 5, 7, 9.


> **`return` statement**
>
> The `return` statement is used to return a value from a function or code block. The last expression in a block is implicitly returned.

```ts
value = {
    x = 1
    if condition return x // Early return if condition is true
    y = 2
    x + y // Returned implicitly
}
// value can either be 1 (early) or 3 (implicit)
```


### Other keywords and operators

Other than the operators and keywords listed above, there are a number of other keywords and operators that can be used in `mini`.
* `is` - Used to match values against patterns and bind them to variables
* `in` - Used to check if a value is in a set of values
* `..` - Used to specify a range of values

> **`is` keyword**
>
> The `is` keyword is used to match values against patterns and bind them to variables.

Use `is` in an if-else statement to pattern match on values and change the control flow of the program depending on the match result.

```ts
if x is number "number"
else if x is string "string"
else if x is bool "bool"
else "unknown"
```

Or more specifically, get the type of the value and bind it to a variable.

```ts
if x is number(n) "number: " + n
else if x is string(s) "string: " + s
else if x is bool(b) "bool: " + b
else "unknown: " + x
```

Can be used to handle optional values.

```fs
if x is Some(v) "some: " + v
else "none"
```

Or match on data types.

```ts
if l is [head | tail] "list: " + head + " " + tail
else
```

> **`in` keyword**
>
> The `in` keyword is used to check if a value is in a set of values.

Check if a value is in a list.

```ts
if x in [1, 2, 3] "in list"
else "not in list"
```

Check if a value is in a range. Read more about the `..` operator below.

```ts
if x in 1..10 "in range"
else "not in range"
```

Check if value is a key in a map. If `x` would be `2` for example, `x` would be in the map and the condition would be true.

```ts
if x in #{1: "one", 2: "two", 3: "three"} "in map"
else "not in map"
```

Check if a value is in a tuple.

```ts
if x in (1, 2, 3) "in tuple"
else "not in tuple"
```

One can also use `in` when iterating over a set of values using a `for` loop.

```ts
for x in [1, 2, 3] print(x)
```


> **`..` Operator**
>
> The `..` operator is used to specify a range of values including the lower and upper bounds.

```ts
for i in 1..10 {
    txt = 'i: ' + i
    print(txt)
}
```

The example above prints the numbers 1 to 10.

It is also possible to generate a lazy sequence of values withouth having to store them in memory by excluding the upper bound.

```ts
for i in 1.. {
    if i > 1000 break
    txt = 'i: ' + i
    print(txt)
}
```

## Contribute! 🎉
Contributions of all kinds are welcome, not only in the form of **code** but also with regards to the official **documentation**, **debugging** help and **tickets/issues** in the bug tracker, support of other users on the **community** forum or the official discord and also **financially**.

If you think something is bad about the `mini` language or the article series written about it, please **help in any way to make it better** instead of complaining about it.

For information about how to go about submitting bug reports or pull requests, please see the project's [contribution guidelines](https://github.com/mini-lang/mini-lang/blob/main/CONTRIBUTING.md).

### 1. Perfecting the language 👑
There is much more to the language than just the syntax, and there are several ways to improve it.
Optimizing the interpreter and compiler is one of the most important aspects of the tooling for a language.
Do consider contributing to the [mini-lang project](https://github.com/mini-lang/mini-lang) to make your own improvements.

Do you have your own ideas for improvements? Are they specialized in a certain area or controversial in nature?
Please create your own version of the language by forking it on GitHub and sharing your changes!

### 2. Improve the documentation 📝
The documentation is a great source of information for anyone who wants to learn the language.
It is also a great source of information for anyone who wants to contribute to the project.

If you are a regular user of the language, you can help improve the documentation by creating a pull request to the official [documentation repository](https://github.com/mini-lang/mini-lang).

### 3. Expand the ecosystem 🏕️
There are numerous ways of contributing to the `mini` language, one of which is to contribute code to the [official repository](https://github.com/mini-lang/mini-lang), but there are also many other ways to contribute.

* Consider building projects in `mini` and publish your projects on GitHub.
* Expand on the tools and libraries that are already available for `mini` and publish your own, look at the todo list and the [third-party tools](/TODO.md#Third-party-tools) section.

### 4. Get involved in the community 🫂
The best way to show support and help is to get involved in the community! There are many ways to get involved, start by joining the [official discord](https://discord.gg/YzjQZjh) and ask questions, share your ideas and discuss the language there! It is a great place to learn about the language and to get help with any issues you might have, or to even help out with the development of the language.

### 5. Improve the article series 📚
If you are a writer and want to contribute to the article series, please see the [contributing to the article series](/CONTRIBUTING.md#Article-series) section.

Other ways to contribute to the article series include:
* Commenting on the articles
* Writing articles about the series
* Writing articles about the language and the project

> ### Citation
> Correctly cite and refer to the `mini` programming language and the article series by using the `🗨️ Cite this repository` button in the right-hand sidebar of this repository.

## Development

Fork the [official repository](https://github.com/mini-lang/mini-lang) and start contributing!
Play around with the code and see how it works. Add your own features and fix bugs.
When you are done, submit a pull request [here](https://github.com/mini-lang/mini-lang/pulls).

Interact with the [community](https://discord.gg/YzjQZjh) and ask questions, share your ideas and discuss the language there!

### Tests

Run all [tests](https://github.com/mini-lang/mini-lang/tree/main/tests) to make sure the language works as expected by running `py test.py` in the root of the repository.

Always create new tests when you add a new feature. This will help us to make sure that the language will continue to work as expected.
New tests in `tests/test_*.py` are discovered automatically by `python test.py`.
Every `mini` code fence in the [v1 guide](docs/v1-guide.md) also runs automatically.
Set `MINI_TUTORIAL_DIR=../mini-lang.github.io` to check the companion v1 examples.

The existing legacy suites export a `run_all` function. If extending that structure,
import the suite in `test.py` and call it as in the example below.

```python
passed &= run_all_list_tests()
```

## License
This project is licensed under the [MIT license](https://github.com/mini-lang/mini-lang/blob/main/LICENSE).
The source code is available on [GitHub](https://github.com/mini-lang/mini-lang).
To modify the code, please fork the project and experiment with the language.
Expanding on the language is highly encouraged. If you have any suggestions, please open an issue or pull request.
