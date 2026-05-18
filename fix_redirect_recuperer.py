with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = """def recuperer_materiel(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id)

    if demande.statut == 'approuvee':
        demande.statut = 'en_cours'
        demande.save()

        for ligne in demande.lignes.all():
            ligne.materiel.etat = 'emprunte'
            ligne.materiel.save()
            log_action(request, 'materiel_recupere', f\"{request.user.username} a recupere '{ligne.materiel.nom}'\", materiel=ligne.materiel)
            Notification.objects.create(
                message=f\"📦 {request.user.username} a récupéré le matériel '{ligne.materiel.nom}'\",
                type='recuperation',
                demande=demande
            )

        messages.success(request, '✅ Matériel récupéré avec succès !')
    else:
        messages.error(request, '❌ Action non autorisée')

    return redirect('mes_demandes')"""

new = """def recuperer_materiel(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id)

    if demande.statut == 'approuvee':
        demande.statut = 'en_cours'
        demande.save()

        for ligne in demande.lignes.all():
            ligne.materiel.etat = 'emprunte'
            ligne.materiel.save()
            log_action(request, 'materiel_recupere', f\"{request.user.username} a remis '{ligne.materiel.nom}' a {demande.utilisateur.username}\", materiel=ligne.materiel, demande=demande)
            Notification.objects.create(
                message=f\"📦 Le materiel '{ligne.materiel.nom}' a ete remis a {demande.utilisateur.username}\",
                type='recuperation',
                demande=demande
            )

        messages.success(request, f'✅ Materiel remis a {demande.utilisateur.username} avec succes !')
    else:
        messages.error(request, '❌ Action non autorisee')

    if request.user.is_staff or request.user.role == 'admin':
        return redirect('gestion_demandes')
    return redirect('mes_demandes')"""

if old in content:
    content = content.replace(old, new)
    print('Correction appliquee!')
else:
    import re
    content = re.sub(
        r'def recuperer_materiel\(request, demande_id\):.*?return redirect\(.mes_demandes.\)',
        new,
        content,
        flags=re.DOTALL
    )
    print('Correction par regex!')

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
