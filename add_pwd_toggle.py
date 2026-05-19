for filename in ['templates/connexion.html', 'templates/connexion_admin.html', 'templates/inscription.html']:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Ajouter bouton oeil sur chaque champ password
    import re
    content = re.sub(
        r'(<input[^>]*type=["\']password["\'][^>]*name=["\']password["\'][^>]*>)',
        r'''<div class="input-group">
                            \1
                            <button type="button" class="btn btn-outline-secondary" onclick="togglePwd(this)" tabindex="-1" style="border-radius:0 8px 8px 0">
                                <i class="fas fa-eye"></i>
                            </button>
                        </div>''',
        content
    )
    content = re.sub(
        r'(<input[^>]*type=["\']password["\'][^>]*name=["\']password2["\'][^>]*>)',
        r'''<div class="input-group">
                            \1
                            <button type="button" class="btn btn-outline-secondary" onclick="togglePwd(this)" tabindex="-1" style="border-radius:0 8px 8px 0">
                                <i class="fas fa-eye"></i>
                            </button>
                        </div>''',
        content
    )

    # Ajouter JS togglePwd avant </body>
    if 'togglePwd' not in content:
        content = content.replace('</body>', '''<script>
function togglePwd(btn) {
    const input = btn.closest('.input-group').querySelector('input');
    const icon = btn.querySelector('i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    }
}
</script>
</body>''')

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'{filename} mis a jour!')
