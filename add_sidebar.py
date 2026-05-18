with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Remplacer la navbar par topbar + sidebar + layout
old_nav = re.search(r'<nav class="navbar.*?</nav>', content, re.DOTALL)
old_main = re.search(r'<div class="container-fluid p-4">', content)

if old_nav and old_main:
    new_header = """<style>
    .sidebar { width: 220px; background: #2c3e50; position: fixed; top: 0; left: 0; height: 100vh; overflow-y: auto; z-index: 1000; }
    .sidebar-brand { padding: 18px 16px; font-weight: 700; color: white; font-size: 0.95rem; border-bottom: 1px solid rgba(255,255,255,0.1); display: block; }
    .sidebar-section { padding: 12px 16px 4px; color: rgba(255,255,255,0.45); font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
    .sidebar-link { display: flex; align-items: center; gap: 10px; padding: 9px 16px; color: rgba(255,255,255,0.8); text-decoration: none; font-size: 0.83rem; border-left: 3px solid transparent; transition: all 0.2s; }
    .sidebar-link:hover { background: rgba(255,255,255,0.1); color: white; border-left-color: #3498db; }
    .sidebar-link i { width: 16px; text-align: center; }
    .sidebar-divider { border-color: rgba(255,255,255,0.1); margin: 4px 0; }
    .topbar { position: fixed; top: 0; left: 220px; right: 0; height: 52px; background: #2c3e50; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; z-index: 999; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
    .page-content { margin-left: 220px; margin-top: 52px; padding: 24px; }
    @media (max-width: 768px) {
        .sidebar { transform: translateX(-100%); transition: transform 0.3s; }
        .sidebar.open { transform: translateX(0); }
        .topbar { left: 0; }
        .page-content { margin-left: 0; }
        .sidebar-toggle { display: block !important; }
        .overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 999; }
        .overlay.open { display: block; }
    }
</style>

<!-- OVERLAY MOBILE -->
<div class="overlay" id="overlay" onclick="closeSidebar()"></div>

<!-- SIDEBAR -->
<div class="sidebar" id="sidebar">
    <a class="sidebar-brand" href="{% url 'dashboard' %}">
        <i class="fas fa-chart-line"></i> UFR Admin
    </a>

    <div class="sidebar-section">Principal</div>
    <a href="{% url 'dashboard' %}" class="sidebar-link"><i class="fas fa-tachometer-alt"></i> Dashboard</a>
    <a href="{% url 'journal_activite' %}" class="sidebar-link"><i class="fas fa-history"></i> Journal d'activite</a>

    <hr class="sidebar-divider">
    <div class="sidebar-section">Materiels</div>
    <a href="{% url 'catalogue' %}" class="sidebar-link"><i class="fas fa-eye"></i> Voir le catalogue</a>
    <a href="{% url 'gestion_catalogue' %}" class="sidebar-link"><i class="fas fa-boxes"></i> Gerer le catalogue</a>
    <a href="{% url 'carte_materiels' %}" class="sidebar-link"><i class="fas fa-map-marker-alt"></i> Carte materiels</a>

    <hr class="sidebar-divider">
    <div class="sidebar-section">Emprunts</div>
    <a href="{% url 'gestion_demandes' %}" class="sidebar-link"><i class="fas fa-clipboard-list"></i> Demandes</a>
    <a href="{% url 'gestion_maintenance' %}" class="sidebar-link"><i class="fas fa-tools"></i> Maintenance</a>

    <hr class="sidebar-divider">
    <div class="sidebar-section">Utilisateurs</div>
    <a href="{% url 'gestion_utilisateurs' %}" class="sidebar-link"><i class="fas fa-users"></i> Utilisateurs</a>
    <a href="/admin/" class="sidebar-link"><i class="fas fa-cog"></i> Admin Django</a>

    <hr class="sidebar-divider">
    <div class="sidebar-section">Exports</div>
    <a href="{% url 'export_excel' %}" class="sidebar-link"><i class="fas fa-file-excel text-success"></i> Export Excel</a>
    <a href="{% url 'export_pdf' %}" class="sidebar-link"><i class="fas fa-file-pdf text-danger"></i> Export PDF</a>
</div>

<!-- TOPBAR -->
<div class="topbar">
    <div class="d-flex align-items-center gap-3">
        <button class="btn btn-sm btn-outline-light sidebar-toggle" style="display:none" onclick="toggleSidebar()">
            <i class="fas fa-bars"></i>
        </button>
        <span class="text-white fw-bold"><i class="fas fa-chart-line"></i> Dashboard Administrateur</span>
    </div>
    <div class="d-flex align-items-center gap-2">
        <span class="text-white small"><i class="fas fa-user"></i> {{ user.username }}</span>
        <a href="{% url 'deconnexion' %}" class="btn btn-outline-danger btn-sm"><i class="fas fa-sign-out-alt"></i> Deconnexion</a>
    </div>
</div>

<!-- PAGE CONTENT -->
<div class="page-content">"""

    # Supprimer l'ancienne navbar
    content = content[:old_nav.start()] + new_header + content[old_main.end():]

    # Ajouter le JS toggle sidebar avant </body>
    js = """
<script>
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
    document.getElementById('overlay').classList.toggle('open');
}
function closeSidebar() {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('overlay').classList.remove('open');
}
</script>"""
    content = content.replace('</body>', js + '\n</body>')

    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Sidebar ajoute!')
else:
    print('Pattern non trouve')
