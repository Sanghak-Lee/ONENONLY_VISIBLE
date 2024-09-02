from __future__ import absolute_import
import os
from decouple import config
from celery import Celery
from celery.schedules import crontab
from django.conf import settings


DEBUG = config('DEBUG', cast=bool)
if DEBUG:
  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djecommerce.settings.development')
else:
  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djecommerce.settings.production')

app = Celery('djecommerce')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# app.conf.beat_schedule = { 
#   # 'djecommerce': { 
#   #   'task': 'djecommerce.celery.dj_debug',
#   #   'schedule': crontab(minute='*/30'),
#   #   },
#   #Every 12H
#   'core': { 
#     'task': 'core.tasks.GET_KAKAO_RESULT',
#         'schedule': crontab(minute=0, hour='*/12'),
#     },
#   }

@app.task(bind=True)
def dj_debug(self):
   print('Request: {0!r}'.format(self.request))