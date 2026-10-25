i = 0
total = 0
while i < 6 {
    i += 1
    if i % 2 == 0 { continue }
    total += i
}
assert(total == 9, "while skips even values")

for row in 1..4 {
    for column in 1..5 {
        if column == 2 { continue }
        if column == 4 { break }
        total += row * column
    }
}
assert(total == 33, "nested control targets the nearest loop")

first_large(values) = {
    for value in values {
        if value > 5 { return value }
    }
    ()
}
assert(first_large([1, 8, 9]) == 8, "return unwinds a loop")
assert(first_large([]) == (), "empty loop falls through")
print(total)
