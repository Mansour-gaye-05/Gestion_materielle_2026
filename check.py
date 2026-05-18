import ast, sys
try:
    with open('gestion/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    ast.parse(content)
    print('OK - pas erreur')
except SyntaxError as e:
    print(f'Erreur ligne {e.lineno}: {e.msg}')
    lines = content.splitlines()
    for i in range(max(0,e.lineno-3), min(len(lines),e.lineno+3)):
        print(f'{i+1}: {repr(lines[i])}')
