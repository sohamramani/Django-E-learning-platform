import logging

from .models import Enrollment
from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from edu_user.models import UserProfile


logger = logging.getLogger(__name__)

# Signal to send an email notification when a user enrolls in a course
@receiver(post_save, sender=Enrollment)
def send_enrollment_notification(sender, instance, created, **kwargs):
    if created:
        subject = 'Course Enrollment Confirmation'
        message = f'You have successfully enrolled in {instance.course.title}.' 
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [instance.student.email]
        send_mail(subject, message, from_email, recipient_list)
        logger.info(f'{instance.student.username} have successfully enrolled in {instance.course.title}. and email send successfully')


# Signal to create a user profile when a user logs in with social auth
@receiver(user_logged_in)
def create_profile(sender, request, user, **kwargs):
    social_auth = user.social_auth.first()
    if social_auth:
        if UserProfile.objects.filter(user=user).exists():
            logger.info('User profile already exists.')
            return
        provider = social_auth.provider
        UserProfile.objects.create(user=user)
        logger.info('user profile created with social auth login')
    else:
        logger.error("User logged in without social auth.")
