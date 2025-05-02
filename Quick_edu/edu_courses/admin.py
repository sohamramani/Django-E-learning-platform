from django.contrib import admin
from .models import Category, Courses


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category, CategoryAdmin)

class CoursesAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'category', 'course_creator')
    search_fields = ('title',)
    list_filter = ('category',)

admin.site.register(Courses, CoursesAdmin)

