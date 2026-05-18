with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '<a href="{% url \'gestion_catalogue\' %}"><i class="fas fa-boxes text-primary"></i> Catalogue materiels</a>',
    '<a class="dropdown-item" href="{% url \'catalogue\' %}"><i class="fas fa-eye text-secondary"></i> Voir le catalogue</a></li><li><a class="dropdown-item" href="{% url \'gestion_catalogue\' %}"><i class="fas fa-boxes text-primary"></i> Gerer le catalogue</a>'
)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Lien catalogue ajoute!')
