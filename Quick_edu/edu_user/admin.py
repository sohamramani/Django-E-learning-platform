from django.contrib import admin
from .models import UserProfile,  Enrollment


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', "gender", "birth_date", "country", "profile_picture", "mobile_number", "resume")
    search_fields = ('user__username', 'user__email')
admin.site.register(UserProfile, UserProfileAdmin)

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'is_active')
    search_fields = ('student__username', 'course__title')
    list_filter = ('is_active',)

admin.site.register(Enrollment, EnrollmentAdmin)