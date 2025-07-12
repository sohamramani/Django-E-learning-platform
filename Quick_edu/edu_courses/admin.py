from .models import Category, Courses
from django.contrib import admin


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created', 'modified')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
admin.site.register(Category, CategoryAdmin)


class CoursesAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'category', 'course_creator')
    search_fields = ('title','course_creator','start_date', 'end_date')
    list_filter = ('created', 'modified','start_date', 'end_date',)
admin.site.register(Courses, CoursesAdmin)

