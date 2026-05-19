with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Ajouter CSS animations
old_style = '    </style>'
new_style = '''
        /* ANIMATIONS */
        @keyframes fadeInUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
        @keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
        @keyframes countUp { from { opacity:0; transform:scale(0.5); } to { opacity:1; transform:scale(1); } }
        @keyframes slideInLeft { from { opacity:0; transform:translateX(-20px); } to { opacity:1; transform:translateX(0); } }

        .stat-card { animation: fadeInUp 0.5s ease forwards; opacity:0; }
        .kpi-card { animation: fadeInUp 0.5s ease forwards; opacity:0; }
        .chart-card { animation: fadeIn 0.6s ease forwards; opacity:0; }
        .data-table { animation: fadeIn 0.6s ease forwards; opacity:0; }
        .sidebar-link { transition: all 0.2s ease; }

        /* Delais pour les stat cards */
        .stat-card:nth-child(1) { animation-delay: 0.05s; }
        .stat-card:nth-child(2) { animation-delay: 0.1s; }
        .stat-card:nth-child(3) { animation-delay: 0.15s; }
        .stat-card:nth-child(4) { animation-delay: 0.2s; }
        .stat-card:nth-child(5) { animation-delay: 0.25s; }
        .stat-card:nth-child(6) { animation-delay: 0.3s; }
        .kpi-card:nth-child(1) { animation-delay: 0.35s; }
        .kpi-card:nth-child(2) { animation-delay: 0.4s; }
        .kpi-card:nth-child(3) { animation-delay: 0.45s; }
        .kpi-card:nth-child(4) { animation-delay: 0.5s; }
        .chart-card { animation-delay: 0.55s; }
        .data-table { animation-delay: 0.6s; }

        /* Hover effects */
        .stat-card { transition: transform 0.2s ease, box-shadow 0.2s ease; cursor: default; }
        .stat-card:hover { transform: translateY(-4px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }
        .kpi-card { transition: transform 0.2s ease; }
        .kpi-card:hover { transform: translateY(-3px); }

        /* Topbar slide down */
        .topbar { animation: fadeInUp 0.4s ease forwards; }
        .sidebar { animation: slideInLeft 0.4s ease forwards; }
    </style>'''

content = content.replace('    </style>', new_style)

# Ajouter animation compteurs pour les valeurs KPI
old_js_end = 'fetchNotifications();\nsetInterval(fetchNotifications, 30000);'
new_js_end = '''fetchNotifications();
setInterval(fetchNotifications, 30000);

// Animation compteurs KPI
function animateValue(el, start, end, duration) {
    if (!el) return;
    let startTime = null;
    const step = (timestamp) => {
        if (!startTime) startTime = timestamp;
        const progress = Math.min((timestamp - startTime) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.floor(eased * (end - start) + start);
        if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
}

// Animer les valeurs stat cards apres chargement
window.addEventListener('load', () => {
    setTimeout(() => {
        document.querySelectorAll('.stat-val').forEach(el => {
            const val = parseInt(el.textContent) || 0;
            el.textContent = '0';
            animateValue(el, 0, val, 1000);
        });
        document.querySelectorAll('.kpi-val').forEach(el => {
            const text = el.textContent.trim();
            const val = parseFloat(text);
            if (!isNaN(val) && !text.includes('j') && !text.includes('%')) {
                el.textContent = '0';
                animateValue(el, 0, val, 800);
            }
        });
    }, 300);
});'''

content = content.replace(old_js_end, new_js_end)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Animations dashboard ajoutees!')
