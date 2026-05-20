with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Ajouter CSS animations
old_style = '</style>'
new_style = '''
        /* ANIMATIONS */
        @keyframes fadeInUp { from { opacity:0; transform:translateY(30px); } to { opacity:1; transform:translateY(0); } }
        @keyframes fadeInLeft { from { opacity:0; transform:translateX(-30px); } to { opacity:1; transform:translateX(0); } }
        @keyframes fadeInRight { from { opacity:0; transform:translateX(30px); } to { opacity:1; transform:translateX(0); } }
        @keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
        @keyframes scaleIn { from { opacity:0; transform:scale(0.8); } to { opacity:1; transform:scale(1); } }
        @keyframes slideDown { from { opacity:0; transform:translateY(-20px); } to { opacity:1; transform:translateY(0); } }
        @keyframes pulse-soft { 0%,100% { transform:scale(1); } 50% { transform:scale(1.05); } }
        @keyframes shimmer { 0% { background-position:-200% center; } 100% { background-position:200% center; } }

        .anim-fade-up { opacity:0; animation: fadeInUp 0.8s ease forwards; }
        .anim-fade-left { opacity:0; animation: fadeInLeft 0.8s ease forwards; }
        .anim-fade-right { opacity:0; animation: fadeInRight 0.8s ease forwards; }
        .anim-fade { opacity:0; animation: fadeIn 0.8s ease forwards; }
        .anim-scale { opacity:0; animation: scaleIn 0.6s ease forwards; }
        .anim-slide-down { opacity:0; animation: slideDown 0.6s ease forwards; }

        .delay-1 { animation-delay: 0.1s; }
        .delay-2 { animation-delay: 0.2s; }
        .delay-3 { animation-delay: 0.3s; }
        .delay-4 { animation-delay: 0.4s; }
        .delay-5 { animation-delay: 0.5s; }
        .delay-6 { animation-delay: 0.6s; }
        .delay-7 { animation-delay: 0.7s; }
        .delay-8 { animation-delay: 0.8s; }

        /* HOVER EFFECTS */
        .access-card { transition: transform 0.3s ease, box-shadow 0.3s ease !important; }
        .access-card:hover { transform: translateY(-8px) !important; box-shadow: 0 25px 60px rgba(0,0,0,0.2) !important; }
        .feature-item { transition: transform 0.3s ease; }
        .feature-item:hover { transform: translateY(-5px); }
        .btn-hero-primary, .btn-hero-secondary { transition: all 0.3s ease !important; }

        /* SHIMMER sur les stats */
        .stat-num { background: linear-gradient(90deg, white 0%, rgba(255,255,255,0.6) 50%, white 100%); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shimmer 3s linear infinite; }

        /* SCROLL REVEAL */
        .reveal { opacity:0; transform:translateY(40px); transition: opacity 0.7s ease, transform 0.7s ease; }
        .reveal.visible { opacity:1; transform:translateY(0); }
        .reveal-left { opacity:0; transform:translateX(-40px); transition: opacity 0.7s ease, transform 0.7s ease; }
        .reveal-left.visible { opacity:1; transform:translateX(0); }
        .reveal-right { opacity:0; transform:translateX(40px); transition: opacity 0.7s ease, transform 0.7s ease; }
        .reveal-right.visible { opacity:1; transform:translateX(0); }
    </style>'''

content = content.replace('    </style>', new_style)

# Ajouter classes animation sur les elements hero
content = content.replace(
    '<div class="hero-badge">',
    '<div class="hero-badge anim-slide-down delay-1">'
)
content = content.replace(
    '<h1 class="hero-title">',
    '<h1 class="hero-title anim-fade-up delay-2">'
)
content = content.replace(
    '<p class="hero-subtitle">',
    '<p class="hero-subtitle anim-fade-up delay-3">'
)
content = content.replace(
    '<div class="hero-btns">',
    '<div class="hero-btns anim-fade-up delay-4">'
)
content = content.replace(
    '<div class="hero-stats">',
    '<div class="hero-stats anim-fade-up delay-5">'
)

# Ajouter reveal sur section acces
content = content.replace(
    '<div class="section-title">',
    '<div class="section-title reveal">'
)

# Ajouter reveal sur chaque feature item
content = content.replace(
    '<div class="feature-item">',
    '<div class="feature-item reveal">'
)

# Ajouter classes stat-num sur les compteurs
content = content.replace(
    '<div class="num" id="count-materiels">',
    '<div class="num stat-num" id="count-materiels">'
)
content = content.replace(
    '<div class="num" id="count-dispo">',
    '<div class="num stat-num" id="count-dispo">'
)
content = content.replace(
    '<div class="num" id="count-users">',
    '<div class="num stat-num" id="count-users">'
)
content = content.replace(
    '<div class="num" id="count-demandes">',
    '<div class="num stat-num" id="count-demandes">'
)

# Ajouter JS scroll reveal avant </script> final
old_script = 'window.addEventListener(\'load\', () => {'
new_script = '''// SCROLL REVEAL
const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
        if (entry.isIntersecting) {
            setTimeout(() => entry.target.classList.add('visible'), i * 100);
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('.reveal, .reveal-left, .reveal-right').forEach(el => {
    revealObserver.observe(el);
});

window.addEventListener(\'load\', () => {'''

content = content.replace(old_script, new_script)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Animations accueil ajoutees!')
