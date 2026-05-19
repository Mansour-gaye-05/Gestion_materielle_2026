for filename in ['templates/espace_etudiant.html', 'templates/mes_demandes.html']:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    anim_css = '''
        /* ANIMATIONS */
        @keyframes fadeInUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
        @keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
        .welcome-card { animation: fadeInUp 0.5s ease forwards; }
        .stat-grid { animation: fadeInUp 0.5s ease 0.1s forwards; opacity:0; }
        .section-card { animation: fadeInUp 0.5s ease 0.2s forwards; opacity:0; }
        .demande-card { animation: fadeInUp 0.4s ease forwards; opacity:0; }
        .demande-card:nth-child(1) { animation-delay: 0.05s; }
        .demande-card:nth-child(2) { animation-delay: 0.1s; }
        .demande-card:nth-child(3) { animation-delay: 0.15s; }
        .demande-card:nth-child(4) { animation-delay: 0.2s; }
        .demande-card:nth-child(5) { animation-delay: 0.25s; }
        .topbar { animation: fadeInUp 0.4s ease forwards; }
        .stat-card { transition: transform 0.2s ease; }
        .stat-card:hover { transform: scale(1.04); }
        .btn-action { transition: transform 0.2s ease, box-shadow 0.2s ease; }
        .btn-action:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.15); }
        .emprunt-item { transition: transform 0.2s ease; }
        .emprunt-item:hover { transform: translateX(4px); }
    '''

    content = content.replace('    </style>', anim_css + '\n    </style>')

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'{filename} - animations ajoutees!')
