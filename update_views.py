# Lire le fichier views.py
with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Ajouter log_action apres les imports si pas deja present
if 'def log_action' not in content:
    log_fn = '''

def log_action(request_or_user, action, description, demande=None, materiel=None):
    from .models import JournalActivite
    if hasattr(request_or_user, 'META'):
        user = request_or_user.user if request_or_user.user.is_authenticated else None
        ip = request_or_user.META.get('REMOTE_ADDR')
    else:
        user = request_or_user
        ip = None
    JournalActivite.objects.create(
        utilisateur=user,
        action=action,
        description=description,
        ip_address=ip,
        demande=demande,
        materiel=materiel
    )

'''
    content = content.replace('# ==================== PAGE D\'ACCUEIL ====================', log_fn + '# ==================== PAGE D\'ACCUEIL ====================')
    print('log_action ajoute')
else:
    print('log_action deja present')

# Ajouter la vue journal si pas deja presente
if 'def journal_activite' not in content:
    journal_view = '''

# ==================== JOURNAL D ACTIVITE ====================

@staff_member_required
def journal_activite(request):
    from .models import JournalActivite
    journaux = JournalActivite.objects.select_related('utilisateur', 'demande', 'materiel').all()
    action_filter = request.GET.get('action')
    user_filter = request.GET.get('utilisateur')
    date_filter = request.GET.get('date')
    if action_filter:
        journaux = journaux.filter(action=action_filter)
    if user_filter:
        journaux = journaux.filter(utilisateur__username__icontains=user_filter)
    if date_filter:
        journaux = journaux.filter(date__date=date_filter)
    from .models import JournalActivite as JA
    context = {
        'journaux': journaux[:200],
        'action_choices': JA.ACTION_CHOICES,
        'total': journaux.count(),
    }
    return render(request, 'journal_activite.html', context)
'''
    content = content + journal_view
    print('vue journal_activite ajoutee')
else:
    print('vue journal_activite deja presente')

# Ajouter logs dans connexion
if "log_action(request, 'connexion'" not in content:
    content = content.replace(
        "login(request, user)\n            if user.role == 'admin' or user.is_superuser:\n                return redirect('dashboard')\n            else:\n                return redirect('espace_etudiant')",
        "login(request, user)\n            log_action(request, 'connexion', f\"{user.username} s'est connecte\")\n            if user.role == 'admin' or user.is_superuser:\n                return redirect('dashboard')\n            else:\n                return redirect('espace_etudiant')"
    )
    print('log connexion ajoute')

# Ajouter log dans inscription
if "log_action(request, 'inscription'" not in content:
    content = content.replace(
        "login(request, utilisateur)\n                messages.success(request, f'Bienvenue {username}",
        "login(request, utilisateur)\n                log_action(request, 'inscription', f'Nouveau compte: {username}')\n                messages.success(request, f'Bienvenue {username}"
    )
    print('log inscription ajoute')

# Ajouter log dans rendre_materiel
if "log_action(request, 'materiel_rendu'" not in content:
    content = content.replace(
        "Notification.objects.create(\n                message=f\"",
        "log_action(request, 'materiel_rendu', f\"{request.user.username} a rendu '{ligne.materiel.nom}'\", materiel=ligne.materiel)\n            Notification.objects.create(\n                message=f\""
    )
    print('log materiel_rendu ajoute')

# Ajouter log dans recuperer_materiel
if "log_action(request, 'materiel_recupere'" not in content:
    content = content.replace(
        "Notification.objects.create(\n                message=f\"\U0001f4e6",
        "log_action(request, 'materiel_recupere', f\"{request.user.username} a recupere '{ligne.materiel.nom}'\", materiel=ligne.materiel)\n            Notification.objects.create(\n                message=f\"\U0001f4e6"
    )
    print('log materiel_recupere ajoute')

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('views.py mis a jour avec succes!')
