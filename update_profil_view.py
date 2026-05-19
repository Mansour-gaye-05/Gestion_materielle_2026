with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = """@login_required
def profil_etudiant(request):
    if request.method == 'POST':
        request.user.email = request.POST.get('email')
        request.user.telephone = request.POST.get('telephone')
        request.user.filiere = request.POST.get('filiere')
        request.user.niveau = request.POST.get('niveau')
        request.user.save()
        messages.success(request, 'Profil mis a jour !')
        return redirect('profil_etudiant')

    return render(request, 'profil_etudiant.html')"""

new = """@login_required
def profil_etudiant(request):
    if request.method == 'POST':
        request.user.email = request.POST.get('email')
        request.user.telephone = request.POST.get('telephone')
        request.user.filiere = request.POST.get('filiere')
        request.user.niveau = request.POST.get('niveau')
        if 'photo_profil' in request.FILES:
            request.user.photo_profil = request.FILES['photo_profil']
        request.user.save()
        messages.success(request, 'Profil mis a jour !')
        return redirect('profil_etudiant')

    return render(request, 'profil_etudiant.html')"""

if old in content:
    content = content.replace(old, new)
    print('Vue profil mise a jour!')
else:
    import re
    content = re.sub(
        r'@login_required\ndef profil_etudiant\(request\):.*?return render\(request, .profil_etudiant\.html.\)',
        new,
        content,
        flags=re.DOTALL
    )
    print('Vue profil mise a jour par regex!')

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
