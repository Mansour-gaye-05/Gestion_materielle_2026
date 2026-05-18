lines = open('templates/dashboard.html', 'r', encoding='utf-8').readlines()

old_line = '        <a href="{% url \'deconnexion\' %}" class="btn btn-outline-light btn-sm"><i class="fas fa-sign-out-alt"></i></a>\n'

new_lines = '''        <div class="notif-bell position-relative" onclick="toggleNotif()">
            <button class="btn btn-outline-light btn-sm">
                <i class="fas fa-bell"></i>
                <span class="notif-badge" id="notif-badge" style="display:none">0</span>
            </button>
            <div class="notif-dropdown" id="notifDropdown">
                <div class="notif-dropdown-header">
                    <span><i class="fas fa-bell"></i> Notifications</span>
                    <span onclick="marquerLues(event)" style="cursor:pointer;font-size:0.75rem;opacity:0.8">Tout lire</span>
                </div>
                <div id="notif-list"><div class="notif-empty">Chargement...</div></div>
            </div>
        </div>
        <a href="{% url 'deconnexion' %}" class="btn btn-outline-danger btn-sm"><i class="fas fa-sign-out-alt"></i> Deconnexion</a>
'''

for i, l in enumerate(lines):
    if 'deconnexion' in l and 'btn-outline-light' in l and 'sign-out' in l:
        lines[i] = new_lines
        print(f'Ligne {i+1} remplacee!')
        break

open('templates/dashboard.html', 'w', encoding='utf-8').write(''.join(lines))
