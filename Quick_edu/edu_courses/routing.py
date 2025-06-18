from django.urls import path
from edu_courses import consumers


# notification urls to disply notification
websocket_urlpatterns = [
        path('ws/enrollments/', consumers.EnrollmentConsumer.as_asgi()),
        path("ws/course_updates/", consumers.CourseNotificationConsumer.as_asgi()),
]