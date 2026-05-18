with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Verifier si bg-custom est defini
if 'bg-custom' in content and '#2c3e50' not in content[:500]:
    print('bg-custom present mais couleur manquante dans style')
else:
    print('OK')

# Afficher le style actuel
import re
style = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
if style:
    print(style.group(1)[:300])
