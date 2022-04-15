a = ()
print("unit =", a, a == ())

b = (1)
print("value =", b)

c = (1, 2)
print("tuple =", c)

d = (1, 2, 3)
print("tuple =", d)

// print(c + d) // Should throw an error because mismatched sizes

print(c + " + (5, 2) =", c + (5, 2))

e = ("test", true)
f = (1, '!')
print(e + " + " + f + " =", e + f)

print("first index in e:", e[0])
print("second index in e:", e[1])
print("first index in f:", f[0])
print("second index in f:", f[1])
