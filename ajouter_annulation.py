# Script: ajouter annulation demande

# 1. MODIFIER LE TEMPLATE mes_demandes.html
content = open('templates/mes_demandes.html', encoding='utf-8').read()
open('templates/mes_demandes.html.bak', 'w', encoding='utf-8').write(content)

# Ajouter bouton Annuler dans la vue MOBILE (card) apres statut en_attente
old_mobile = "{% if demande.statut == 'en_attente' %}"
new_mobile = """{% if demande.statut == 'en_attente' %}
                        <button class="btn btn-action" style="background:#e74c3c;color:white"
                            data-bs-toggle="modal" data-bs-target="#annulerModal{{ demande.id }}">
                            <i class="fas fa-times-circle"></i> Annuler la demande
                        </button>"""

# Ajouter le modal d'annulation avant </body>
modal_annuler = """
{% for demande in demandes %}
{% if demande.statut == 'en_attente' %}
<div class="modal fade" id="annulerModal{{ demande.id }}" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content" style="border-radius:16px;overflow:hidden">
            <div class="modal-header" style="background:#e74c3c;color:white">
                <h6 class="modal-title" style="font-family:Manrope;font-weight:700">
                    <i class="fas fa-times-circle me-2"></i>Annuler la demande
                </h6>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <p class="mb-1">Voulez-vous vraiment annuler la demande <strong>#{{ demande.id }}</strong> ?</p>
                <p class="text-muted small">Cette action est irreversible.</p>
            </div>
            <div class="modal-footer" style="border:none;gap:8px">
                <button type="button" class="btn btn-outline-secondary btn-sm" data-bs-dismiss="modal" style="border-radius:20px">Fermer</button>
                <form method="post" action="{% url 'annuler_demande' demande.id %}">
                    {% csrf_token %}
                    <button type="submit" class="btn btn-danger btn-sm px-4" style="border-radius:20px;font-family:Inter;font-weight:600">
                        <i class="fas fa-times-circle me-1"></i> Confirmer l'annulation
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endif %}
{% endfor %}
"""

import re

# Ajouter bouton annuler dans carte mobile - apres la div en_attente
content = content.replace(
    "{% if demande.statut == 'en_attente' %}",
    """{% if demande.statut == 'en_attente' %}
                        <button class="btn btn-action mt-2" style="background:#e74c3c;color:white;border-radius:25px"
                            data-bs-toggle="modal" data-bs-target="#annulerModal{{ demande.id }}">
                            <i class="fas fa-times-circle me-1"></i> Annuler la demande
                        </button>""",
    1
)
print("Bouton mobile ajoute")

# Ajouter bouton annuler dans tableau desktop - apres statut en_attente
content = content.replace(
    "{% if demande.statut == 'en_attente' %}\n                                <span",
    """{% if demande.statut == 'en_attente' %}
                                <button class="btn btn-sm btn-danger ms-1" data-bs-toggle="modal" data-bs-target="#annulerModal{{ demande.id }}" style="border-radius:20px;font-size:0.75rem;padding:4px 12px">
                                    <i class="fas fa-times-circle"></i> Annuler
                                </button>
                                <span""",
    1
)
print("Bouton desktop ajoute")

# Ajouter les modals avant </body>
content = content.replace('</body>', modal_annuler + '\n</body>')
print("Modals ajoutes")

open('templates/mes_demandes.html', 'w', encoding='utf-8').write(content)
print("Template mis a jour!")

# 2. AJOUTER LA VUE dans views.py
views_content = open('gestion/views.py', encoding='utf-8').read()
open('gestion/views.py.bak', 'w', encoding='utf-8').write(views_content)

vue_annuler = '''
@login_required
def annuler_demande(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id, utilisateur=request.user)
    if demande.statut == 'en_attente':
        demande.statut = 'annulee'
        demande.save()
        log_action(request, 'demande_annulee',
            f"{request.user.username} a annule la demande #{demande.id}",
            demande=demande)
        messages.success(request, f'Demande #{demande.id} annulee avec succes.')
    else:
        messages.error(request, 'Cette demande ne peut pas etre annulee.')
    return redirect('mes_demandes')

'''

# Inserer avant def mes_demandes
views_content = views_content.replace('def mes_demandes(request):', vue_annuler + 'def mes_demandes(request):')
open('gestion/views.py', 'w', encoding='utf-8').write(views_content)
print("Vue annuler_demande ajoutee!")

# 3. AJOUTER L'URL
urls_content = open('Gestion_emprunt_materiels_SI/urls.py', encoding='utf-8').read()
open('Gestion_emprunt_materiels_SI/urls.py.bak', 'w', encoding='utf-8').write(urls_content)

if 'annuler_demande' not in urls_content:
    urls_content = urls_content.replace(
        "path('mes-demandes/', views.mes_demandes, name='mes_demandes'),",
        "path('mes-demandes/', views.mes_demandes, name='mes_demandes'),\n    path('demande/<int:demande_id>/annuler/', views.annuler_demande, name='annuler_demande'),"
    )
    open('Gestion_emprunt_materiels_SI/urls.py', 'w', encoding='utf-8').write(urls_content)
    print("URL ajoutee!")
else:
    print("URL deja presente")

print("\nTout est pret! Redemarrez le serveur.")
