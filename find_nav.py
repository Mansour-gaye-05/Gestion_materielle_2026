lines = open('templates/dashboard.html', 'r', encoding='utf-8').readlines()
for i, l in enumerate(lines, 1):
    if 70 <= i <= 80:
        print(f'{i}: {repr(l)}')
