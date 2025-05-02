from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from edu_courses.models import Courses
from django_extensions.db.models import TimeStampedModel

class UserProfile(TimeStampedModel):
    GENDER_CHOICES = {
        "male" : "male",
        "female" : "female",
    }
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    gender = models.CharField("gender", choices = GENDER_CHOICES, blank=True, null=True, max_length=10)
    birth_date = models.DateField("birth date", blank=True, null=True)
    country = CountryField("country", blank=True, null=True)
    profile_picture = models.ImageField("profile picture", upload_to = 'profile_picture/', blank=True, null=True)
    mobile_number = PhoneNumberField("mobile number", unique = True, region="IN")
    resume = models.FileField("resume", upload_to='resumes/', blank=True, null=True)

    def __str__(self):
        return f"{self.user}"

    def get_age(self):
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    class Meta:
        db_table = 'user_profile'
        verbose_name = 'User Profile'

class Enrollment(TimeStampedModel):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments', verbose_name='student')
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name='enrollments', verbose_name='course')
    is_active = models.BooleanField("is active", default=True)

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"

    class Meta:
        db_table = 'enrollment'
        verbose_name = 'Enrollment'
        unique_together = ('student', 'course')
