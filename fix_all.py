import re

with open('gestion/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed = 0
for i, line in enumerate(lines):
    # log_action avec 4 espaces alors que la ligne suivante a 8 espaces
    if line.startswith('    log_action') and not line.startswith('        log_action'):
        lines[i] = '    ' + line  # ajoute 4 espaces pour arriver a 8
        fixed += 1
        print(f'Ligne {i+1} corrigee: {repr(lines[i][:60])}')

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print(f'{fixed} correction(s) appliquee(s) !')
