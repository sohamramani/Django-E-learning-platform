from __future__ import absolute_import, unicode_literals


import logging


from .models import Enrollment
from .tokens import account_activation_token
from celery import shared_task
from datetime import datetime,date,timedelta
from django.conf import settings
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from edu_courses.models import Courses
from Quick_edu.celery import app


logger = logging.getLogger(__name__)


# Daily Enrollment Report Mail sending
@shared_task
def send_mail_task():
    logger.info("Daily Enrollment Report Mail sending.....")
    enrollments = Enrollment.objects.filter(created__date=timezone.now().date()).count()
    subject = 'Daily Enrollment Report'
    message = f"Daily Report for {datetime.today().strftime('%d-%m-%Y')}\n\n"
    message += f'Total new enrollments today: {enrollments}'
    send_mail(subject, message, settings.EMAIL_HOST_USER, ['sohamramani20@gmail.com'], fail_silently=False)
    logger.info("Daily Enrollment Report Mail has been sent.....")   


# Course End Date Reminder Mail sending
@shared_task
def send_reminder_courses():
    logger.info("Course End Date Reminder Mail sending.....")
    course = Courses.objects.all()
    course_name = list(course)
    today = date.today()
    two_days_from_now = today + timedelta(days=2)
    
    for name in course_name:
        students = User.objects.all()
        course_enddate = name.end_date
        for student in students:
            if course_enddate == two_days_from_now:
                subject = 'Course End Date Reminder'
                message = f"Course name :{name} , Course End Date :{course_enddate}\n\n"
                message += f'Course is ending soon'
                send_mail(subject, message, settings.EMAIL_HOST_USER, [student.email], fail_silently=False)
                logger.info("Course End Date Reminder Mail has been sent.....")
            else:
                return logger.info("Course is not ending soon.....")


# welcome email sending
@app.task(bind=True)
def send_welcome_email(self, user_email, user_name):
    subject = 'Welcome to Quick edu!'
    message = f'Hi {user_name},\n\nThank you for registering!'
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [user_email], fail_silently=False)
    logger.info('Welcome Email sent successfully.....') 


# Become an Instructor Email sending
@app.task(bind=True)
def send_become_an_instructor_email(self, admin_email, user_email, user_name):
    subject = 'Request to Become Instructor'
    message = f'Username: {user_name},\n Email: {user_email},\n\n I want to become an instructor...............'
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [admin_email], fail_silently=False)
    logger.info('become instructor email sent successfully.....')


# Password Reset Email sending
@shared_task
def send_reset_password_email_task(userpk,email):
        user1 = User.objects.get(id=userpk)
        reset_link = f"{settings.BASE_URL}/reset-password/confirm/"
        html_message = render_to_string('auth/password_reset_email.html', {
        'reset_link': reset_link,
        'user': user1.username,
        'domain': "127.0.0.1:8000",
        'uid': urlsafe_base64_encode(force_bytes(userpk)),
        'token': account_activation_token.make_token(user1),
        'protocol': "http"
        })
        plain_message = strip_tags(html_message)
        send_mail(
            'Password Reset Request',
            plain_message,
            settings.EMAIL_HOST_USER,
            [email],
            html_message=html_message
        )
        return {"status": True}
