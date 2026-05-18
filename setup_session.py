with open('Gestion_emprunt_materiels_SI/settings.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'SESSION_COOKIE_AGE' not in content:
    content += """
# Session timeout
SESSION_COOKIE_AGE = 1800  # 30 minutes
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
"""

with open('Gestion_emprunt_materiels_SI/settings.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Session timeout configure!')
