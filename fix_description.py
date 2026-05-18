with open('templates/catalogue.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Ajouter la description apres les quantites dans chaque carte materiel
old = '''                            <div class="d-flex gap-2 mt-1">
                                <small class="text-muted" style="font-size:0.7rem">Total: {{ materiel.quantite_totale }}</small>
                                <small class="{% if materiel.quantite_disponible > 0 %}text-success{% else %}text-danger{% endif %}" style="font-size:0.7rem">Dispo: {{ materiel.quantite_disponible }}</small>
                            </div>'''

new = '''                            <div class="d-flex gap-2 mt-1">
                                <small class="text-muted" style="font-size:0.7rem">Total: {{ materiel.quantite_totale }}</small>
                                <small class="{% if materiel.quantite_disponible > 0 %}text-success{% else %}text-danger{% endif %}" style="font-size:0.7rem">Dispo: {{ materiel.quantite_disponible }}</small>
                            </div>
                            {% if materiel.description %}
                            <p class="text-muted mt-1 mb-0" style="font-size:0.72rem">{{ materiel.description|truncatechars:80 }}</p>
                            {% endif %}'''

if old in content:
    content = content.replace(old, new)
    print('Description ajoutee!')
else:
    print('Pattern non trouve - cherche alternative')
    # Chercher autre pattern
    import re
    idx = content.find('quantite_disponible')
    print(content[idx:idx+200])

with open('templates/catalogue.html', 'w', encoding='utf-8') as f:
    f.write(content)
