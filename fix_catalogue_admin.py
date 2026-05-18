with open('templates/catalogue.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Proteger les liens dans le bottom nav mobile
content = content.replace(
    '<a href="{% url \'nouvelle_demande\' %}" style="color:white">',
    '{% if not user.is_staff %}<a href="{% url \'nouvelle_demande\' %}" style="color:white">'
)
content = content.replace(
    '<span>Demander</span>\n    </a>\n    <a href="{% url \'mes_demandes\' %}">',
    '<span>Demander</span>\n    </a>{% endif %}\n    {% if not user.is_staff %}<a href="{% url \'mes_demandes\' %}">'
)
content = content.replace(
    '<a href="{% url \'chatbot\' %}"><i class="fas fa-robot"></i><span>IA</span></a>',
    '<a href="{% url \'chatbot\' %}"><i class="fas fa-robot"></i><span>IA</span></a>{% endif %}'
)

# 2. Proteger les liens dans le sidebar menu
content = content.replace(
    '{% if user.is_authenticated %}\n                    <a href="{% url \'nouvelle_demande\' %}" class="list-group-item list-group-item-action">',
    '{% if user.is_authenticated and not user.is_staff %}\n                    <a href="{% url \'nouvelle_demande\' %}" class="list-group-item list-group-item-action">'
)

with open('templates/catalogue.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Catalogue mis a jour!')
