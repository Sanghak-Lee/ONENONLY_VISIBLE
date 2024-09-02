import os
from decouple import config
from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

DJANGO_APPS = [
    'jet',
    'jet.dashboard',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',    
    'django.contrib.humanize', 

    #allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.kakao',
    'allauth.socialaccount.providers.naver',
]

PROJECT_APPS =[
    'core',
    'user',
    'auction',
    'artist',
]

THIRD_PARTY_APPS=[
    'phonenumber_field',
    'rest_framework',
    'drf_yasg',
    'storages',
    'sass_processor',
    'django_celery_beat',
    'django_celery_results',
]

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + THIRD_PARTY_APPS


# SWAGGER_SETTINGS = {
#     'DEFAULT_AUTO_SCHEMA_CLASS': 'djecommerce.inspectors.MyAutoSchema',
# }

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

FILE_UPLOAD_HANDLERS = [
 'django.core.files.uploadhandler.TemporaryFileUploadHandler'
]  # Removed MemoryFileUploadHandler

AUTH_USER_MODEL = "user.Users"

ROOT_URLCONF = 'djecommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
                os.path.join(BASE_DIR, 'templates'),
                ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'djecommerce.custom_context_processors.googleanalytics'
            ],
        },
    },
]

#SASS
SASS_PROCESSOR_ENABLED=True
SASS_OUTPUT_STYLE='compact'

#SESSION AND COOKIE(8H)
SESSION_COOKIE_AGE = 60 * 60 * 8

#WSGI SETTINGS
WSGI_APPLICATION = 'djecommerce.wsgi.application'


#REGION, TIMEZONE
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_L10N = True
USE_TZ = False

LANGUAGES = [
    ('ko', _('Korean')),
    ('en', _('English')),
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'


#배포환경에서 (DEBUG=False) 참조
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')

# 개발환경 manage.py 에서 참조
STATICFILES_DIRS = []

STATICFILES_FINDERS=(
    'sass_processor.finders.CssFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_root')

#AWS S3
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEYID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_REGION = config('AWS_REGION')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = '%s.s3.%s.amazonaws.com' % (config('AWS_STORAGE_BUCKET_NAME'), config('AWS_REGION'))
AWS_DEFAULT_ACL = None
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024000000 # value in bytes 1GB here
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024000000

DEFAULT_FILE_STORAGE = 'djecommerce.storages.MediaStorage'
#STATICFILES_STORAGE = 'djecommerce.storages.StaticStorage'
MEDIAFILES_LOCATION = 'Media 파일'
STATICFILES_LOCATION = 'Static 파일'

# AUTHENTICATION
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
    
)

#AUTH_PASSWORD
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}
]

#?
SITE_ID = 2


#EMAIL send, Gmail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_TIMEOUT=60
EMAIL_PORT = 587
EMAIL_HOST = 'smtp.outlook.office365.com'
EMAIL_HOST_USER = "support@onenonly.io"
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


#Invitation <-> Adpater
# ACCOUNT_ADAPTER = 'invitations.models.InvitationsAdapter'
ACCOUNT_ADAPTER = 'user.adapter.MyAccountAdapter'
ACCOUNT_FORMS = {'signup': 'user.forms.MyCustomSignupForm'}
SOCIALACCOUNT_FORMS = {'signup': 'user.forms.MyCustomSocialSignupForm'}
SOCIALACCOUNT_ADAPTER = 'user.adapter.MySocialAccountAdapter'

#ACCOUNT_CONFIG
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
LOGIN_REDIRECT_URL = '/'
ACCOUNT_SESSION_REMEMBER = None
SOCIALACCOUNT_AUTO_SIGNUP = True
ACCOUNT_LOGOUT_ON_GET = True
#VARIABLES_SETTINGS
SECRET_KEY = config('SECRET_KEY')

#LOCALE
LOCALE_PATHS=[os.path.join(BASE_DIR, 'locale')]

#CELERY
DJANGO_CELERY_BEAT_TZ_AWARE = False
REDIS_LOCATION_PRIMARY=config('REDIS_LOCATION_PRIMARY')
REDIS_LOCATION_REPLICA=config('REDIS_LOCATION_REPLICA')
CELERY_ALWAYS_EAGER = False

#CELERY_BROKER_URL -> dev, prod
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

#JET
JET_THEMES = [
    {
        'theme': 'default', # theme folder name
        'color': '#47bac1', # color of the theme's button in user menu
        'title': 'Default' # theme title
    },
    {
        'theme': 'revenor', # theme folder name
        'color': '#F14B6F', # color of the theme's button in user menu
        'title': '레브너 시그니처' # theme title
    },    
    {
        'theme': 'green',
        'color': '#44b78b',
        'title': 'Green'
    },
    {
        'theme': 'light-green',
        'color': '#2faa60',
        'title': 'Light Green'
    },
    {
        'theme': 'light-violet',
        'color': '#a464c4',
        'title': 'Light Violet'
    },
    {
        'theme': 'light-blue',
        'color': '#5EADDE',
        'title': 'Light Blue'
    },
    {
        'theme': 'light-gray',
        'color': '#222',
        'title': 'Light Gray'
    }
]
JET_SIDE_MENU_COMPACT = True
JET_INDEX_DASHBOARD = 'djecommerce.dashboard.CustomIndexDashboard'
# JET_MODULE_GOOGLE_ANALYTICS_CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, 'client_secrets.json')

#PHONE
PHONENUMBER_DEFAULT_REGION = 'KR'