for filename in ['templates/connexion_admin.html']:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    old = '''        <div class="mb-3">
            <label class="form-label">Mot de passe</label>
            <div class="input-icon">
                <i class="fas fa-lock"></i>
                <div class="input-group">
                            <input type="password" name="password" class="form-control" placeholder="Mot de passe" autocomplete="off" required>
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
                <input type="password" name="password" class="form-control" placeholder="Mot de passe" autocomplete="off" required style="border-left:none">
                <button type="button" class="btn" onclick="togglePwd(this)" tabindex="-1"
                        style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);border-left:none;color:rgba(255,255,255,0.5);border-radius:0 12px 12px 0">
                    <i class="fas fa-eye"></i>
                </button>
            </div>
        </div>'''

    if old in content:
        content = content.replace(old, new)
        print(f'{filename} - corrige!')
    else:
        print(f'{filename} - pattern non trouve')

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

# Meme correction pour inscription
with open('templates/inscription.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
# Supprimer les icones toggle dupliquees dans inscription
content = re.sub(r'<i class="fas fa-eye toggle-icon" id="togglePassword.*?"></i>', '', content)
content = re.sub(r"document\.getElementById\('togglePassword.*?\}\);", '', content, flags=re.DOTALL)

# Corriger les input-group dans input-icon
content = re.sub(
    r'<div class="input-icon">\s*<i class="fas fa-lock"></i>\s*<div class="input-group">(.*?)</div>\s*</div>',
    lambda m: '<div class="input-group">' + m.group(1) + '</div>',
    content,
    flags=re.DOTALL
)

with open('templates/inscription.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('inscription.html corrige!')
