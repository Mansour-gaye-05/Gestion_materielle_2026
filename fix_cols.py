with open('templates/catalogue.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '<div class="col-6 col-md-4 col-lg-3">',
    '<div class="col-12 col-md-4">'
)

with open('templates/catalogue.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
