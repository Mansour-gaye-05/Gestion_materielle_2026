with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

old_nav = re.search(r'<nav class="navbar.*?</nav>', content, re.DOTALL)
if old_nav:
    new_nav = """<nav class="navbar navbar-dark bg-custom px-3">
    <span class="navbar-brand fw-bold"><i class="fas fa-chart-line"></i> Dashboard Admin — UFR Sciences</span>
    <div class="d-flex gap-2 align-items-center">
        <span class="text-white small me-2"><i class="fas fa-user"></i> {{ user.username }}</span>

        <!-- Dropdown Gestion -->
        <div class="dropdown">
            <button class="btn btn-outline-light btn-sm dropdown-toggle" data-bs-toggle="dropdown">
                <i class="fas fa-cogs"></i> Gestion
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
                <li><a class="dropdown-item" href="{% url 'gestion_catalogue' %}"><i class="fas fa-boxes text-primary"></i> Catalogue materiels</a></li>
                <li><a class="dropdown-item" href="{% url 'gestion_demandes' %}"><i class="fas fa-clipboard-list text-warning"></i> Demandes</a></li>
                <li><a class="dropdown-item" href="{% url 'gestion_maintenance' %}"><i class="fas fa-tools text-danger"></i> Maintenance</a></li>
                <li><a class="dropdown-item" href="{% url 'gestion_utilisateurs' %}"><i class="fas fa-users text-info"></i> Utilisateurs</a></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="{% url 'carte_materiels' %}"><i class="fas fa-map text-success"></i> Carte materiels</a></li>
                <li><a class="dropdown-item" href="{% url 'journal_activite' %}"><i class="fas fa-history text-secondary"></i> Journal activite</a></li>
            </ul>
        </div>

        <!-- Dropdown Exports -->
        <div class="dropdown">
            <button class="btn btn-outline-light btn-sm dropdown-toggle" data-bs-toggle="dropdown">
                <i class="fas fa-download"></i> Exports
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
                <li><a class="dropdown-item" href="{% url 'export_excel' %}"><i class="fas fa-file-excel text-success"></i> Export Excel</a></li>
                <li><a class="dropdown-item" href="{% url 'export_pdf' %}"><i class="fas fa-file-pdf text-danger"></i> Export PDF</a></li>
            </ul>
        </div>

        <a href="/admin/" class="btn btn-outline-light btn-sm"><i class="fas fa-cog"></i> Admin</a>
        <a href="{% url 'deconnexion' %}" class="btn btn-outline-danger btn-sm"><i class="fas fa-sign-out-alt"></i></a>
    </div>
</nav>"""
    content = content[:old_nav.start()] + new_nav + content[old_nav.end():]
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Navbar mise a jour!')
else:
    print('Navbar non trouvee')
