import os
from decouple import config
from django.core.wsgi import get_wsgi_application
DEBUG = config('DEBUG', default=False, cast=bool)
if DEBUG:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djecommerce.settings.development')    
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djecommerce.settings.production')
application = get_wsgi_application()
