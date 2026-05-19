with open('templates/profil_etudiant.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Ajouter enctype au formulaire profil
content = content.replace(
    '<form method="post" action="{% url \'profil_etudiant\' %}">',
    '<form method="post" action="{% url \'profil_etudiant\' %}" enctype="multipart/form-data">'
)

# 2. Remplacer avatar par photo si disponible + ajouter input file
old_avatar = '''    <div class="text-center mb-4">
        <div class="avatar-circle">{{ user.username|first|upper }}</div>
        <h5 style="font-family:Manrope;font-weight:800;color:var(--primary)">{{ user.username }}</h5>
        <span class="badge" style="background:var(--accent);border-radius:12px;font-size:0.72rem">{{ user.get_role_display }}</span>
    </div>'''

new_avatar = '''    <div class="text-center mb-4">
        {% if user.photo_profil %}
            <img src="{{ user.photo_profil.url }}" alt="Photo profil"
                 style="width:80px;height:80px;border-radius:50%;object-fit:cover;border:3px solid var(--primary);margin-bottom:12px">
        {% else %}
            <div class="avatar-circle">{{ user.username|first|upper }}</div>
        {% endif %}
        <h5 style="font-family:Manrope;font-weight:800;color:var(--primary)">{{ user.username }}</h5>
        <span class="badge" style="background:var(--accent);border-radius:12px;font-size:0.72rem">{{ user.get_role_display }}</span>
    </div>'''

content = content.replace(old_avatar, new_avatar)

# 3. Ajouter champ photo dans le formulaire avant le bouton submit
content = content.replace(
    '<button type="submit" class="btn-submit">',
    '''<div class="mb-3">
                    <label class="form-label"><i class="fas fa-camera me-1"></i> Photo de profil</label>
                    <input type="file" name="photo_profil" class="form-control" accept="image/*" onchange="previewPhoto(this)" style="border-radius:10px">
                    <div id="photoPreview" class="mt-2 text-center" style="display:none">
                        <img id="previewImg" src="" alt="Preview" style="width:70px;height:70px;border-radius:50%;object-fit:cover;border:3px solid var(--primary)">
                    </div>
                </div>
                <button type="submit" class="btn-submit">'''
)

# 4. Ajouter JS preview photo
content = content.replace(
    'function togglePwd(btn) {',
    '''function previewPhoto(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('previewImg').src = e.target.result;
            document.getElementById('photoPreview').style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function togglePwd(btn) {'''
)

with open('templates/profil_etudiant.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('profil_etudiant.html mis a jour!')
