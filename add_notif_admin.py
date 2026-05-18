with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Ajouter styles cloche
old_style = '    </style>'
new_style = '''        /* CLOCHE */
        .notif-bell { position: relative; }
        .notif-badge { position: absolute; top: -6px; right: -6px; background: #e74c3c; color: white; border-radius: 50%; width: 18px; height: 18px; font-size: 0.65rem; display: flex; align-items: center; justify-content: center; font-weight: 700; animation: pulse 2s infinite; }
        @keyframes pulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.2); } }
        .notif-dropdown { position: absolute; right: 0; top: 40px; width: 320px; background: white; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); z-index: 9999; display: none; }
        .notif-dropdown.open { display: block; }
        .notif-dropdown-header { padding: 12px 16px; background: #2c3e50; color: white; border-radius: 12px 12px 0 0; display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; font-weight: 700; }
        .notif-item-dd { padding: 10px 16px; border-bottom: 1px solid #f0f0f0; font-size: 0.8rem; }
        .notif-item-dd.unread { border-left: 3px solid #e74c3c; background: #fff8f8; }
        .notif-empty { padding: 20px; text-align: center; color: #999; font-size: 0.82rem; }
    </style>'''

content = content.replace(old_style, new_style)

# Ajouter cloche dans la topbar avant deconnexion
old_topbar_end = '<a href="{% url \'deconnexion\' %}" class="btn btn-outline-danger btn-sm"><i class="fas fa-sign-out-alt"></i> Deconnexion</a>'
new_topbar_end = '''<div class="notif-bell position-relative" onclick="toggleNotif()">
            <button class="btn btn-outline-light btn-sm">
                <i class="fas fa-bell"></i>
                <span class="notif-badge" id="notif-badge" style="display:none">0</span>
            </button>
            <div class="notif-dropdown" id="notifDropdown">
                <div class="notif-dropdown-header">
                    <span><i class="fas fa-bell"></i> Notifications systeme</span>
                    <span onclick="marquerLues(event)" style="cursor:pointer;font-size:0.75rem;opacity:0.8">Tout lire</span>
                </div>
                <div id="notif-list"><div class="notif-empty">Chargement...</div></div>
            </div>
        </div>
        <a href="{% url \'deconnexion\' %}" class="btn btn-outline-danger btn-sm"><i class="fas fa-sign-out-alt"></i> Deconnexion</a>'''

content = content.replace(old_topbar_end, new_topbar_end)

# Ajouter endpoint admin pour notifications (toutes les notifs pas seulement user)
notif_js = """
<script>
function getCookie(name) {
    let v = null;
    document.cookie.split(';').forEach(c => {
        c = c.trim();
        if (c.startsWith(name + '=')) v = decodeURIComponent(c.substring(name.length + 1));
    });
    return v;
}

async function fetchNotifications() {
    try {
        const r = await fetch('/notifications/admin/');
        const data = await r.json();
        const badge = document.getElementById('notif-badge');
        const list = document.getElementById('notif-list');

        if (data.count > 0) {
            badge.style.display = 'flex';
            badge.textContent = data.count > 9 ? '9+' : data.count;
        } else {
            badge.style.display = 'none';
        }

        if (data.notifications.length === 0) {
            list.innerHTML = '<div class="notif-empty"><i class="fas fa-bell-slash d-block mb-2" style="font-size:1.5rem"></i>Aucune notification</div>';
        } else {
            list.innerHTML = data.notifications.map(n =>
                '<div class="notif-item-dd ' + (!n.lu ? 'unread' : '') + '">' +
                '<div style="font-size:0.72rem;color:#999">' + n.date + '</div>' +
                '<div>' + n.message.substring(0, 90) + (n.message.length > 90 ? '...' : '') + '</div>' +
                '</div>'
            ).join('');
        }
    } catch(e) {}
}

function toggleNotif() {
    const dd = document.getElementById('notifDropdown');
    dd.classList.toggle('open');
    if (dd.classList.contains('open')) fetchNotifications();
}

async function marquerLues(e) {
    e.stopPropagation();
    await fetch('/notifications/admin/lues/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
    });
    document.getElementById('notif-badge').style.display = 'none';
    fetchNotifications();
}

document.addEventListener('click', function(e) {
    const bell = document.querySelector('.notif-bell');
    if (bell && !bell.contains(e.target)) {
        document.getElementById('notifDropdown').classList.remove('open');
    }
});

fetchNotifications();
setInterval(fetchNotifications, 30000);
</script>"""

content = content.replace('</body>', notif_js + '\n</body>')

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Cloche admin ajoutee!')
