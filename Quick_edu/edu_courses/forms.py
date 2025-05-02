from urllib import request
from django import forms
from .models import Courses, Category
from django.contrib.auth.models import User

class CourseForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput)
    description = forms.CharField(widget=forms.Textarea, required=False)
    start_date = forms.DateField(widget=forms.SelectDateWidget(years=range(2025, 2100)),required=False)
    end_date = forms.DateField(widget=forms.SelectDateWidget(years=range(2025, 2100)),required=False)
    image = forms.ImageField(required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    course_creator = forms.ModelChoiceField(queryset=User.objects.none())
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        self.fields['course_creator'].queryset = User.objects.filter(id=request.user.id)

