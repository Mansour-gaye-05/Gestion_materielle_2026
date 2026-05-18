with open('Gestion_emprunt_materiels_SI/settings.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'from pathlib import Path\nimport os',
    'from pathlib import Path\nimport os\nfrom dotenv import load_dotenv\nload_dotenv()'
)
content = content.replace(
    "SECRET_KEY = 'django-insecure-p59b+hth)%0ds2hc1cla9@qky&0d^r\$@@zz#p75i8hq5uf#bq-'",
    "SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-p59b+hth')"
)
content = content.replace(
    "GROQ_API_KEY = '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'",
    "GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')"
)

with open('Gestion_emprunt_materiels_SI/settings.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('.env configure!')
