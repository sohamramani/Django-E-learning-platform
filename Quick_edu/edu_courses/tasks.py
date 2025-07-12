from __future__ import absolute_import, unicode_literals

import logging
import pandas as pd

from .models import Courses
from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMessage
from edu_user.models import UserProfile
from io import BytesIO


logger = logging.getLogger(__name__)


# course_report exccel file email sending
@shared_task
def export_course_excel(admin_email):
    cache_key_course = f"course_report_"
    cached_report_course = cache.get(cache_key_course)
    
    if cached_report_course:
        email = EmailMessage(
            'Course Report (Cached)',
            'Please find attached the cached course report.',
            'from@example.com',
            [admin_email],
        )
        email.attach('course_report_cached.xlsx', cached_report_course.read(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        email.send()
        logger.info("Course Data retrieved from cache.....")
        return cached_report_course
    else:
        logger.info("Course Data not in cache, generating new report.....")
        objs = Courses.objects.all()
        payload = []
        for obj in objs:
            payload.append({
                'course id' : obj.id,
                'title' : obj.title,
                'description':obj.description,
                'start_date':obj.start_date ,
                'end_date':obj.end_date ,
                'image':obj.image, 
                'category':obj.category ,
                'course_creator':obj.course_creator ,
            })

        df = pd.DataFrame(payload)
        df.index = df.index + 1
        excel_file_course = BytesIO()
        with pd.ExcelWriter(excel_file_course,  engine='xlsxwriter') as writer:
            df.to_excel(writer, index_label="index", sheet_name='Courses Data')
        
        excel_file_course.seek(0)
        cache.set(cache_key_course, excel_file_course, timeout=60 * 60)
        excel_file_course.seek(0)

        email = EmailMessage(
                'Course Report',
                'Please find attached the student report.',
                'from@example.com',
                [admin_email],
        )
        email.attach('course_report.xlsx', excel_file_course.read(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        email.send()
        logger.info(f"Course Report email sent.....")
    return excel_file_course.read()


# student_report exccel file email sending
@shared_task
def export_student_excel(admin_email):
    cache_key_student = f"student_report_"
    cached_report_student = cache.get(cache_key_student)
    
    if cached_report_student:
        email = EmailMessage(
            'Student Report (Cached)',
            'Please find attached the cached course report.',
            'from@example.com',
            [admin_email],
        )
        email.attach('student_report_cached.xlsx', cached_report_student.read(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        email.send()
        logger.info("Student Data retrieved from cache......")
        return cached_report_student
    else:
        logger.info("Student Data not in cache, generating new report.....")
        objk = UserProfile.objects.filter(user__is_staff=False)
        payload = []
        for obj in objk:
                payload.append({
                    'user id' : obj.user.id,
                    'username' : obj.user.username,
                    'email':obj.user.email,
                    'first_name':obj.user.first_name ,
                    'last_name':obj.user.last_name ,
                    'gender':obj.gender, 
                    'country':obj.country.name ,
                    'profile_picture':obj.profile_picture ,
                    'birth_date':obj.birth_date, 
                    'mobile_number':obj.mobile_number, 
                    'resume':obj.resume,
                })
        
        df = pd.DataFrame(payload)
        df.index = df.index + 1
        excel_file_student = BytesIO()
        with pd.ExcelWriter(excel_file_student,  engine='xlsxwriter') as writer:
            df.to_excel(writer, index_label="index", sheet_name='Student Data')
        excel_file_student.seek(0)
        
        cache.set(cache_key_student, excel_file_student, timeout=60 * 60)
        excel_file_student.seek(0)
        
        email = EmailMessage(
            'Student Report',
            'Please find attached the student report.',
            'from@example.com',
            [admin_email],
        )
        email.attach('student_report.xlsx', excel_file_student.read(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        email.send()
        logger.info(f"Student Report email sent.....")
    return excel_file_student.read()