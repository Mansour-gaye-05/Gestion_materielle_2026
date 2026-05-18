with open('templates/mes_demandes.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Supprimer le modal mal place hors de la boucle
import re
content = re.sub(
    r'\n<!-- MODAL PANNE -->.*?{% endif %}\n',
    '\n',
    content,
    flags=re.DOTALL
)

# Remettre le modal juste avant la fermeture de la card-view loop
# Chercher la fin de chaque demande-card et ajouter le modal avant
old = """        </div><!-- /.demande-card -->

        {% empty %}"""

new = """        </div><!-- /.demande-card -->

        <!-- MODAL PANNE -->
        {% if demande.statut == 'en_cours' %}
        <div class="modal fade" id="panneModal{{ demande.id }}" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content" style="border-radius:16px;overflow:hidden">
                    <form method="post" action="{% url 'signaler_panne_emprunt' demande.id %}">
                        {% csrf_token %}
                        <div class="modal-header bg-danger text-white">
                            <h6 class="modal-title"><i class="fas fa-exclamation-triangle"></i> Signaler une panne</h6>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p class="small text-muted mb-2">
                                Materiel : <strong>{% for l in demande.lignes.all %}{{ l.materiel.nom }}{% if not forloop.last %}, {% endif %}{% endfor %}</strong>
                            </p>
                            <label class="form-label small fw-bold">Description du probleme :</label>
                            <textarea name="description" class="form-control" rows="4"
                                      placeholder="Ex: ne s allume plus, ecran casse, mesures incorrectes..."
                                      required style="border-radius:10px"></textarea>
                            <small class="text-muted mt-1 d-block">
                                <i class="fas fa-info-circle"></i> Un technicien sera informe immediatement.
                            </small>
                        </div>
                        <div class="modal-footer border-0 pt-0">
                            <button type="button" class="btn btn-outline-secondary btn-sm" data-bs-dismiss="modal">Annuler</button>
                            <button type="submit" class="btn btn-danger btn-sm px-4" style="border-radius:20px">Signaler</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        {% endif %}

        {% empty %}"""

if old in content:
    content = content.replace(old, new)
    print('Modal remis dans la boucle!')
else:
    print('Pattern non trouve')

with open('templates/mes_demandes.html', 'w', encoding='utf-8') as f:
    f.write(content)
