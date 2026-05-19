for filename in ['templates/connexion_admin.html', 'templates/inscription.html']:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Verifier si togglePwd existe
    if 'togglePwd' not in content:
        print(f'{filename} - pas de togglePwd, on skip')
        continue

    # Verifier si la fonction JS existe
    if 'function togglePwd' not in content:
        content = content.replace(
            '</body>',
            '''<script>
function togglePwd(btn) {
    const group = btn.closest('.input-group');
    const input = group.querySelector('input[type="password"], input[type="text"]');
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
</body>'''
        )
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'{filename} - fonction ajoutee!')
    else:
        print(f'{filename} - deja present')
