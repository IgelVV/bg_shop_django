import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bg_shop.settings')

app = Celery('bg_shop')

# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()