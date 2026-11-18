import os
from django.core.wsgi import get_wsgi_application

# Указываем Django, где лежат настройки (папка config)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()