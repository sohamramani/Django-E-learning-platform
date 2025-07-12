from django.urls import path
from edu_courses import utils
from edu_courses import views


urlpatterns = [
    path("create_courses_api/", views.create_courses_api, name="create_courses_api"),
    path("create_courses/", views.CourseCreateView.as_view(), name="create_courses"), 
    
    
    path("list_api/", views.course_list_api, name="course_list_api"),
    path("list/", views.CourseListView.as_view(), name="course_list"),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'), 
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('dashboard/', views.CourseDashboardView.as_view(), name='course_dashboard'),

    # random courses and enrolls genration
    path('random_courses/', utils.random_courses, name='random_courses'),
    path('random_enrolls/', utils.random_enrolls, name='random_enrolls'),
]
