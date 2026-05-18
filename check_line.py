lines = open('gestion/views.py', 'r', encoding='utf-8').readlines()
for i, l in enumerate(lines, 1):
    if 1005 <= i <= 1015:
        print(f'{i}: {repr(l)}')
