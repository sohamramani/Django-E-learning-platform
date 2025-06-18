from .models import UserProfile,  Enrollment, RequestLog, Order
from django.contrib import admin

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', "gender", "country", "mobile_number",'created', 'modified')
    search_fields = ('user__username', 'user__email',"mobile_number")
admin.site.register(UserProfile, UserProfileAdmin)


class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'is_active', 'created', 'modified')
    search_fields = ('student__username', 'course__title')
    list_filter = ('is_active',)
admin.site.register(Enrollment, EnrollmentAdmin)


class RequestLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'path', 'method', 'created', 'modified')
    search_fields = ('user__username', 'path', 'method')
    list_filter = ('user',)
admin.site.register(RequestLog, RequestLogAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'amount', 'status', 'provider_order_id', 'payment_id', 'signature_id')
    search_fields = ('name__username', 'status')
    list_filter = ('status',)
admin.site.register(Order, OrderAdmin)
