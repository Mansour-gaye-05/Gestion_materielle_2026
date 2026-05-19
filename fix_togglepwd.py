with open('templates/connexion.html', 'r', encoding='utf-8') as f:
    content = f.read()

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

with open('templates/connexion.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
