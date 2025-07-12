from edu_user.models import UserProfile
from django import forms
from django_countries.fields import CountryField
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as __
from phonenumber_field.formfields import SplitPhoneNumberField


User = get_user_model()


def validate_file_size(value):
        filesize = value.size
        if filesize > 5242880: # 5MB
                raise ValidationError("The maximum file size allowed is 5MB")


class SignupForm(UserCreationForm):
        email = forms.EmailField(validators=[validate_email])
        first_name = forms.CharField(required = False)
        last_name = forms.CharField(required = False)
        gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES,widget=forms.RadioSelect(),required = False)
        birth_date = forms.DateField(widget=forms.SelectDateWidget(years=range(1900, 2024)),required = False)
        country = CountryField(blank_label='select country').formfield(required = False)
        profile_picture = forms.ImageField(required = False)
        mobile_number = SplitPhoneNumberField(region=None, required = False)
        resume = forms.FileField(required = False, validators=[validate_file_size])
        
        
        class Meta:
                model = User
                fields = ['username', 'email', 'first_name', 'last_name', 'password1' ,'password2', 
                        'gender','birth_date','country', 'profile_picture', 'resume', 'mobile_number']
        
        def clean_profile_picture(self):
                profile_picture = self.cleaned_data.get('profile_picture')
                if profile_picture:
                        if not profile_picture.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                                raise ValidationError("Only PNG, JPG, and JPEG files are allowed.")
                        return profile_picture
                return None
        
        def clean_mobile_number(self):
                mobile_number = self.cleaned_data.get('mobile_number')
                if mobile_number:
                        if not mobile_number.is_valid():
                                raise ValidationError("Enter a valid phone number.")
                        return mobile_number
                return None
        
        def clean_resume(self):
                resume = self.cleaned_data.get('resume')
                if resume:
                        if not resume.name.lower().endswith(('.pdf', '.doc', '.docx')):
                                raise ValidationError("Only PDF, DOC, and DOCX files are allowed.")
                        return resume
                return None


class OTPVerificationForm(forms.Form):
        otp = forms.CharField(max_length=6)
        
        def clean_otp(self):
                otp = self.cleaned_data.get('otp')
                if not otp.isdigit() or len(otp) != 6:
                        raise forms.ValidationError("OTP must be a 6-digit number.")
                return otp

class PasswordResetRequestForm(forms.Form):
        email = forms.CharField(label="Email or Username", max_length=254)
        
        def clean_email(self):
                email = self.cleaned_data.get('email')
                if not User.objects.filter(email=email).exists():
                        raise forms.ValidationError("No user with this email address exists.")
                return email
        
class SetPasswordForm(forms.Form):
        new_password1 = forms.CharField(
                label="New password",
                widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                strip=False,
                help_text="",
        )
        new_password2 = forms.CharField(
                label="Confirm new password",
                strip=False,
                widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        )
        def clean(self):
                cleaned_data = super().clean()
                new_password1 = cleaned_data.get("new_password1")
                new_password2 = cleaned_data.get("new_password2")

                if new_password1 and new_password2 and new_password1 != new_password2:
                        raise forms.ValidationError("The two password fields didn't match.")
                return cleaned_data
