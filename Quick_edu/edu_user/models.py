from .utils import PaymentStatus
from datetime import date
from django_countries.fields import CountryField
from django_extensions.db.models import TimeStampedModel
from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields import CharField
from django.utils.translation import gettext_lazy as _
from edu_courses.models import Courses
from phonenumber_field.modelfields import PhoneNumberField

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
    mobile_number = PhoneNumberField("mobile number", region="IN")
    resume = models.FileField("resume", blank=True, null=True, upload_to="resume")
    otp = models.CharField("otp", max_length=6, blank=True, null=True)
    
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



class RequestLog(TimeStampedModel):
        user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
        path = models.CharField(max_length=200)
        method = models.CharField(max_length=10)

        def __str__(self):
            return f"{self.user} - {self.path}"
        
        



class Order(models.Model):
    name = CharField(_("Customer Name"), max_length=254, blank=False, null=False)
    amount = models.FloatField(_("Amount"), null=False, blank=False)
    status = CharField(
        _("Payment Status"),
        default=PaymentStatus.PENDING,
        max_length=254,
        blank=False,
        null=False,
    )
    provider_order_id = models.CharField(_("Order ID"), max_length=40, null=False, blank=False)
    payment_id = models.CharField(_("Payment ID"), max_length=36, null=False, blank=False)
    signature_id = models.CharField(_("Signature ID"), max_length=128, null=False, blank=False)

    def __str__(self):
        return f"{self.id}-{self.name}-{self.status}"