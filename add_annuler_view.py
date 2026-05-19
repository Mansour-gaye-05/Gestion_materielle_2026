with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

annuler_view = '''

# ==================== ANNULER DEMANDE ====================

@login_required
def annuler_demande(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id, utilisateur=request.user)

    if demande.statut in ['en_attente', 'approuvee']:
        ancien_statut = demande.statut
        demande.statut = 'refusee'
        demande.motif_refus = f"Annulee par l etudiant le {timezone.now().strftime('%d/%m/%Y a %H:%M')}"
        demande.save()

        # Remettre le materiel disponible si approuvee
        if ancien_statut == 'approuvee':
            for ligne in demande.lignes.all():
                ligne.materiel.etat = 'disponible'
                ligne.materiel.save()

        # Annuler la reservation
        from .models import Reservation
        Reservation.objects.filter(demande=demande).update(statut='annulee')

        log_action(request, 'demande_refusee', f"{request.user.username} a annule sa demande #{demande.id}", demande=demande)
        messages.success(request, f'Demande #{demande.id} annulee avec succes.')
    else:
        messages.error(request, 'Cette demande ne peut pas etre annulee.')

    return redirect('mes_demandes')
'''

content += annuler_view
with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Vue annuler_demande ajoutee!')
