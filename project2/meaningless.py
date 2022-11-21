c = [1, 2, 3]
# c = c + [4, 5]
del(c[1])

print(c)
print(c[0])
print(c[1:])
print(c[2:])
print(c[3:])

d = [11, 22]
d.remove(22)
print(d)
# print(len(c[4:]))