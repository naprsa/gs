# run: celery worker -A core  --beat -S django --loglevel=info
import os
from celery import Celery
from icecream import ic
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.beat_scheduler = "django_celery_beat.schedulers.DatabaseScheduler"
# app.conf.beat_schedule = {
#     "add-every-minute": {
#         "task": "stats.tasks.collect_disk_info_task",
#         "schedule": crontab(),
#         # "args": (16, 16),
#     },
# }
app.conf.timezone = "Europe/Moscow"
