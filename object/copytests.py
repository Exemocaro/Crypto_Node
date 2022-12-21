
original = {
    'a': 1,
    'b': 2,
    'c': 3
}

original2 = {
    'd': 4,
    'e': 5,
    'f': 6
}

copy = original.copy()
copy2 = original2

copy['a'] = 4
copy.pop('b')

copy2['d'] = 7
copy2.pop('e')

print(original)   # Will print {'a': 1, 'b': 2, 'c': 3}
print(copy)       # Will print {'a': 4, 'c': 3}
print(original2)  # Will print {'d': 7, 'f': 6}
print(copy2)      # Will print {'d': 7, 'f': 6}