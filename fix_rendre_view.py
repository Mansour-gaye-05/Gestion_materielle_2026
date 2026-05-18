# Corriger aussi rendre_materiel dans views.py pour rediriger admin vers gestion_demandes
with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "if request.user.is_staff or request.user.is_superuser:\n        return redirect('gestion_demandes')\n    return redirect('mes_demandes')",
    "if request.user.is_staff or request.user.is_superuser:\n        return redirect('gestion_demandes')\n    return redirect('mes_demandes')"
)

# Aussi corriger rendre_materiel pour enlever restriction utilisateur
old = "def rendre_materiel(request, demande_id):\n    demande = get_object_or_404(Demande, id=demande_id, utilisateur=request.user)"
new = "def rendre_materiel(request, demande_id):\n    demande = get_object_or_404(Demande, id=demande_id)"

if old in content:
    content = content.replace(old, new)
    print('Restriction utilisateur retiree de rendre_materiel!')
else:
    print('Deja corrige')

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
