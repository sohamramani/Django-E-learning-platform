from __future__ import absolute_import, unicode_literals

import os


from celery import Celery
from celery.schedules import crontab
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Quick_edu.settings')
app = Celery('Quick_edu', broker='redis://localhost:6379/0')
app.conf.enable_utc=False
app.conf.update(timezone='Asia/Kolkata')
app.config_from_object(settings, namespace='CELERY')
# Celery Beat tasks registration
app.conf.beat_schedule = {
    'Send_mail_to_Client_course_reminder': {
        'task': 'edu_user.tasks.send_reminder_courses',
        'schedule': 30, # every 30 seconds it will be called
        # 'schedule': crontab(minute=0, hour=10),  # Run at 10 AM daily 
    },
    'Send_mail_to_Client_daily_enroll': {
        'task': 'edu_user.tasks.send_mail_task',
        'schedule': 30,  # every 30 seconds it will be called
        # 'schedule': crontab(minute=0, hour=10),  # Run at 10 AM daily
        },
}
app.autodiscover_tasks()
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')