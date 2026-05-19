with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_view = '''

# ==================== CHANGER MOT DE PASSE ====================

@login_required
def changer_mot_de_passe(request):
    if request.method == 'POST':
        ancien = request.POST.get('ancien_mdp')
        nouveau = request.POST.get('nouveau_mdp')
        confirmer = request.POST.get('confirmer_mdp')

        if not request.user.check_password(ancien):
            messages.error(request, 'Ancien mot de passe incorrect.')
        elif nouveau != confirmer:
            messages.error(request, 'Les nouveaux mots de passe ne correspondent pas.')
        elif len(nouveau) < 6:
            messages.error(request, 'Le mot de passe doit contenir au moins 6 caracteres.')
        else:
            request.user.set_password(nouveau)
            request.user.save()
            log_action(request, 'connexion', f'{request.user.username} a change son mot de passe')
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Mot de passe change avec succes !')
            return redirect('profil_etudiant')

    return redirect('profil_etudiant')
'''

content += new_view
with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Vue changer_mot_de_passe ajoutee!')
