with open('gestion/models.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "    telephone = models.CharField(max_length=15, blank=True, null=True)",
    "    telephone = models.CharField(max_length=15, blank=True, null=True)\n    photo_profil = models.ImageField(upload_to='profil_photos/', blank=True, null=True)"
)

with open('gestion/models.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Champ photo_profil ajoute!')
