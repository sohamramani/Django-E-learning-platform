from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
# from django.contrib.auth import views as auth_views


urlpatterns = [
    path("create_courses/", views.create_course, name="create_courses"), 
    path("list/", views.course_list, name="course_list"),
    path('course_detail/<int:course_id>/', views.course_detail, name='course_detail'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),

    # path("login/", views.LoginView.as_view(), name="login"),
    # path("profile/", views.ProfileView.as_view(), name="profile"),
    # path("logout/", views.LogoutView.as_view(), name="logout"),
    # path('password_change/', views.change_password, name='password_change'),
    # path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)