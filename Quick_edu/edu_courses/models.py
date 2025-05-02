from urllib import request
from django.db import models
from django.contrib.auth.models import User
from django_extensions.db.models import TimeStampedModel
from django.utils.text import slugify

# Create your models here.
class Category(TimeStampedModel):
    name = models.CharField("name", max_length=255)
    description = models.TextField("description", blank=True, null=True)
    slug = models.SlugField("slug", unique=True)
    def save(self, *args, **kwargs):
            self.slug = slugify(self.name)
            super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        db_table = 'category'
        verbose_name = 'Category'
        
class Courses(TimeStampedModel):
    title = models.CharField("title", max_length=255)
    description = models.TextField("description", blank=True, null=True)
    start_date = models.DateField("start date", blank=True, null=True)
    end_date = models.DateField("end date", blank=True, null=True)
    image = models.ImageField("image", upload_to='course_image/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    course_creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    
    def __str__(self):
        return f"{self.title}"
    
    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'

