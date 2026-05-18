with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '<canvas id="evolutionChart" height="100"></canvas>',
    '<canvas id="evolutionChart" height="60"></canvas>'
)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
