from django import forms
from django.contrib.auth import get_user_model
from phonenumber_field.formfields import PhoneNumberField
from django_countries.fields import CountryField
from phonenumber_field.widgets import RegionalPhoneNumberWidget
from .models import UserProfile
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordChangeForm

User = get_user_model()

class SignupForm(forms.Form):
    username = forms.CharField(
                error_messages={
            'required': 'We need your email address to contact you.',
            'invalid': 'Please enter a valid email address.'
        }
)
    email = forms.EmailField(
                error_messages={
            'required': 'We need your email address to contact you.',
            'invalid': 'Please enter a valid email address.'
        }
)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(required = False)
    last_name = forms.CharField(required = False)
    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES,widget=forms.RadioSelect(),required = False)
    birth_date = forms.DateField(widget=forms.SelectDateWidget(years=range(1900, 2024)),required = False)
    country = CountryField(blank_label='select country').formfield(required = False)
    profile_picture = forms.ImageField(required = False)
    mobile_number = PhoneNumberField(widget=RegionalPhoneNumberWidget)
    resume = forms.FileField(required = False)

    def clean(self):
            cleaned_data = super().clean()
            password = cleaned_data.get('field1')
            confirm_password = cleaned_data.get('field2')
            if password != confirm_password:
                raise ValidationError('Password and Confirm Password do not match')
            return cleaned_data

class OTPVerificationForm(forms.Form):
        otp = forms.CharField(max_length=6)

class CustomPasswordChangeForm(PasswordChangeForm):
        class Meta:
            model = User
            wedgets = {}