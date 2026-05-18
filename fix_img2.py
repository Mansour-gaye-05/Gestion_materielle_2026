with open('templates/catalogue.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '.card-img-top { height: 220px; object-fit: contain; object-position: center; cursor: pointer; border-radius: 14px 14px 0 0; background: #f8f9fa; padding: 10px; }',
    '.card-img-top { height: 220px; object-fit: cover; object-position: center; cursor: pointer; border-radius: 14px 14px 0 0; width: 100%; }'
)

with open('templates/catalogue.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
