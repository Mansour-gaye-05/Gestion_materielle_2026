with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = """        Restitution.objects.create(
            demande=demande,
            etat_materiel="Bon état",
            observations=f"Materiel rendu par {request.user.username} le {timezone.now().strftime('%d/%m/%Y à %H:%M')}"
        )"""

new = """        Restitution.objects.get_or_create(
            demande=demande,
            defaults={
                'etat_materiel': "Bon etat",
                'observations': f"Materiel rendu par {request.user.username} le {timezone.now().strftime('%d/%m/%Y a %H:%M')}"
            }
        )"""

if old in content:
    content = content.replace(old, new)
    print('Correction appliquee!')
else:
    import re
    content = re.sub(
        r'Restitution\.objects\.create\(\s*demande=demande,\s*etat_materiel=.*?\)',
        """Restitution.objects.get_or_create(
            demande=demande,
            defaults={
                'etat_materiel': 'Bon etat',
                'observations': f'Materiel rendu par {request.user.username}'
            }
        )""",
        content,
        flags=re.DOTALL
    )
    print('Correction par regex!')

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
