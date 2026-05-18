with open('templates/catalogue.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# 1. Supprimer le sidebar (col-md-2 avec sidebar-menu)
content = re.sub(
    r'<!-- SIDEBAR MENU.*?</div>\s*</div>\s*\n',
    '',
    content,
    flags=re.DOTALL
)

# 2. Changer col-md-10 en col-12
content = content.replace('<div class="col-md-10">', '<div class="col-12">')

# 3. Remplacer description tronquee par description avec modal
old_desc = '''                            {% if materiel.description %}
                            <p class="text-muted mt-1 mb-0" style="font-size:0.72rem">{{ materiel.description|truncatechars:80 }}</p>
                            {% endif %}'''

new_desc = '''                            {% if materiel.description %}
                            <p class="text-muted mt-1 mb-0" style="font-size:0.72rem">
                                {{ materiel.description|truncatechars:60 }}
                                {% if materiel.description|length > 60 %}
                                <a href="#" style="font-size:0.7rem" data-bs-toggle="modal" data-bs-target="#descModal{{ materiel.id }}">lire plus</a>
                                {% endif %}
                            </p>
                            {% endif %}'''

content = content.replace(old_desc, new_desc)

# 4. Ajouter modal description apres chaque modal image
old_modal_end = '''                {% endif %}
                {% empty %}'''

new_modal_end = '''                {% endif %}

                {% if materiel.description and materiel.description|length > 60 %}
                <div class="modal fade" id="descModal{{ materiel.id }}" tabindex="-1">
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content" style="border-radius:14px;overflow:hidden">
                            <div class="modal-header" style="background:#2c3e50;color:white">
                                <h6 class="modal-title"><i class="fas fa-info-circle"></i> {{ materiel.nom }}</h6>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <p class="mb-2">{{ materiel.description }}</p>
                                <hr>
                                <div class="row small text-muted">
                                    <div class="col-6"><i class="fas fa-tag"></i> {{ materiel.categorie.libelle|default:"Non categorise" }}</div>
                                    <div class="col-6"><i class="fas fa-circle"></i> {{ materiel.get_etat_display }}</div>
                                    <div class="col-6 mt-1"><i class="fas fa-box"></i> Total: {{ materiel.quantite_totale }}</div>
                                    <div class="col-6 mt-1"><i class="fas fa-check"></i> Dispo: {{ materiel.quantite_disponible }}</div>
                                </div>
                            </div>
                            <div class="modal-footer border-0 pt-0">
                                {% if user.is_authenticated and materiel.etat == "disponible" and materiel.quantite_disponible > 0 and not user.is_staff %}
                                <a href="{% url "nouvelle_demande" %}?materiel_id={{ materiel.id }}" class="btn btn-sm" style="background:#2c3e50;color:white;border-radius:20px">
                                    <i class="fas fa-shopping-cart"></i> Demander
                                </a>
                                {% endif %}
                                <button type="button" class="btn btn-sm btn-outline-secondary" data-bs-dismiss="modal" style="border-radius:20px">Fermer</button>
                            </div>
                        </div>
                    </div>
                </div>
                {% endif %}

                {% empty %}'''

content = content.replace(old_modal_end, new_modal_end)

with open('templates/catalogue.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Catalogue mis a jour!')
