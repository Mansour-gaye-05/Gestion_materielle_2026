with open('templates/connexion.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''        <div class="mb-3">
            <label class="form-label">Mot de passe</label>
            <div class="input-icon">
                <i class="fas fa-lock"></i>
                <div class="input-group">
                            <input type="password" name="password" id="password" class="form-control" placeholder="Votre mot de passe" required>
                            <button type="button" class="btn btn-outline-secondary" onclick="togglePwd(this)" tabindex="-1" style="border-radius:0 8px 8px 0">
                                <i class="fas fa-eye"></i>
                            </button>
                        </div>
            </div>
        </div>'''

new = '''        <div class="mb-3">
            <label class="form-label">Mot de passe</label>
            <div class="input-group">
                <span class="input-group-text" style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);border-right:none;color:rgba(255,255,255,0.4)">
                    <i class="fas fa-lock"></i>
                </span>
                <input type="password" name="password" class="form-control" placeholder="Votre mot de passe" required style="border-left:none">
                <button type="button" class="btn" onclick="togglePwd(this)" tabindex="-1"
                        style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);border-left:none;color:rgba(255,255,255,0.5);border-radius:0 12px 12px 0">
                    <i class="fas fa-eye"></i>
                </button>
            </div>
        </div>'''

if old in content:
    content = content.replace(old, new)
    print('Champ password corrige!')
else:
    import re
    content = re.sub(
        r'<div class="mb-3">\s*<label class="form-label">Mot de passe</label>.*?</div>\s*</div>',
        new,
        content,
        flags=re.DOTALL,
        count=1
    )
    print('Corrige par regex!')

# Ajouter JS togglePwd avant </body>
if 'togglePwd' not in content:
    content = content.replace('</body>', '''<script>
function togglePwd(btn) {
    const group = btn.closest('.input-group');
    const input = group.querySelector('input');
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

with open('templates/connexion.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('connexion.html mis a jour!')
