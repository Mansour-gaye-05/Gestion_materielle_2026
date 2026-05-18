with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = '<a href="/admin/" class="btn btn-outline-light btn-sm ms-2"><i class="fas fa-cog"></i> Admin</a>'
new = '<a href="/admin/" class="btn btn-outline-light btn-sm ms-2"><i class="fas fa-cog"></i> Admin</a>\n                <a href="{% url \'journal_activite\' %}" class="btn btn-outline-light btn-sm ms-2"><i class="fas fa-history"></i> Journal</a>'

if 'journal_activite' not in content:
    content = content.replace(old, new)
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Lien Journal ajoute!')
else:
    print('Deja present')
