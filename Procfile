web: gunicorn --bind :8000 djecommerce.wsgi:application
celery_worker: celery -A djecommerce.celery.app worker --concurrency=1 --loglevel=INFO -n worker.%%h
celery_beat: celery -A djecommerce.celery.app beat --scheduler django_celery_beat.schedulers:DatabaseScheduler --loglevel=INFO