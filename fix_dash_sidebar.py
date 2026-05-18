with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# 1. Supprimer les styles sidebar
content = re.sub(r'/\* TOPBAR \*/.*?/\* MOBILE \*/.*?}\s*}', '', content, flags=re.DOTALL)

# 2. Remplacer topbar + sidebar par navbar simple
old_nav = re.search(r'<!-- TOPBAR -->.*?<!-- MAIN CONTENT -->', content, re.DOTALL)
if old_nav:
    new_nav = """<nav class="navbar navbar-dark bg-custom px-3">
    <span class="navbar-brand fw-bold"><i class="fas fa-chart-line"></i> Dashboard Admin — UFR Sciences</span>
    <div class="d-flex gap-2 align-items-center">
        <span class="text-white small"><i class="fas fa-user"></i> {{ user.username }}</span>
        <a href="{% url 'gestion_catalogue' %}" class="btn btn-outline-light btn-sm"><i class="fas fa-boxes"></i> Catalogue</a>
        <a href="{% url 'gestion_demandes' %}" class="btn btn-outline-light btn-sm"><i class="fas fa-clipboard-list"></i> Demandes</a>
        <a href="{% url 'gestion_maintenance' %}" class="btn btn-outline-light btn-sm"><i class="fas fa-tools"></i> Maintenance</a>
        <a href="{% url 'gestion_utilisateurs' %}" class="btn btn-outline-light btn-sm"><i class="fas fa-users"></i> Utilisateurs</a>
        <a href="{% url 'journal_activite' %}" class="btn btn-outline-light btn-sm"><i class="fas fa-history"></i> Journal</a>
        <a href="/admin/" class="btn btn-outline-light btn-sm"><i class="fas fa-cog"></i> Admin</a>
        <a href="{% url 'deconnexion' %}" class="btn btn-outline-light btn-sm"><i class="fas fa-sign-out-alt"></i></a>
    </div>
</nav>

<!-- MAIN CONTENT -->"""
    content = content[:old_nav.start()] + new_nav + content[old_nav.end():]
    print('Navbar remplacee!')
else:
    print('Pattern non trouve')

# 3. Supprimer overlay sidebar
content = re.sub(r'<!-- SIDEBAR OVERLAY.*?-->\s*<div class="sidebar-overlay".*?</div>\s*', '', content, flags=re.DOTALL)

# 4. Supprimer sidebar
content = re.sub(r'<!-- SIDEBAR -->\s*<div class="sidebar".*?</div>\s*', '', content, flags=re.DOTALL)

# 5. Remplacer main-content par container-fluid simple
content = content.replace('<div class="main-content">', '<div class="container-fluid p-4">')

# 6. Supprimer la fonction toggleSidebar
content = re.sub(r'function toggleSidebar\(\).*?\}', '', content, flags=re.DOTALL)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Dashboard sidebar supprime!')
