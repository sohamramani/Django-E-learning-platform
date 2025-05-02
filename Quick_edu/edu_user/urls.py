from django.urls import path
from django import views
# from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("signup/", views.signup_view, name="signup"), 
    path("login/", views.login_view, name="login"),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path("profile/", views.profile_view, name="profile"),
    path("logout/", views.logout_view, name="logout"),
    path('password_change/', views.change_password, name='password_change'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)