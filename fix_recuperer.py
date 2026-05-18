with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = """def recuperer_materiel(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id, utilisateur=request.user)"""

new = """def recuperer_materiel(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id)"""

if old in content:
    content = content.replace(old, new)
    print('Correction appliquee!')
else:
    print('Pattern non trouve')

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
