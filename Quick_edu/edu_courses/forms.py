from .models import Courses
from django import forms


class CourseForm(forms.ModelForm):
    class Meta:
        model = Courses
        fields = ['title', 'description', 'start_date', 'end_date', 'image', 'category']