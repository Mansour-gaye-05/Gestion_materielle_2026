with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "demande__statut__in=['approuvee', 'en_cours'],",
    "demande__statut='en_cours',"
)

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Carte corrigee!')
