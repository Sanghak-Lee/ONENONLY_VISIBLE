from .base import *

DEBUG = config('DEBUG', cast=bool)

ALLOWED_HOSTS = ['127.0.0.1', 'revenor.io', 'onenonly.io', '*']

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": ("rest_framework.pagination.PageNumberPagination",),
    "PAGE_SIZE": 10,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "djecommerce.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES":("rest_framework.renderers.JSONRenderer",),
}


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT')
    },
    'OPTIONS': {
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        'charset': 'utf8mb4',  # 테이블 생성 자동으로 해줄때 쓸 인코딩,, 이거안하면 밑에꺼해도 효과 엑스
        'use_unicode': True,
    },
}

#CELERY
CELERY_BROKER_URL = f"redis://{REDIS_LOCATION_PRIMARY}"
CACHES = { 
    "default": { 
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": [ 
                        f"redis://{REDIS_LOCATION_PRIMARY}", 
                        f"redis://{REDIS_LOCATION_REPLICA}" 
                ],
                "OPTIONS": { 
                    "CLIENT_CLASS": "django_redis.client.DefaultClient", 
                    'SOCKET_TIMEOUT': 5,
                    'SOCKET_CONNECT_TIMEOUT': 5,                    
                    },
                } 
        }

#SENTRY Logger
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
sentry_sdk.init(
    dsn=config('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=0.4,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

#Save logging