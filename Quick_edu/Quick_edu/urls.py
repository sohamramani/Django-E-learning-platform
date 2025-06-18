"""
URL configuration for Quick_edu project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, re_path
from edu_user.views import home
from graphene_file_upload.django import FileUploadGraphQLView



urlpatterns = [
    path("", home, name="home"),
    path('admin/', admin.site.urls),
    
    # edu_user urls
    path('users/', include('edu_user.urls')),
    
    # edu_courses urls
    path('courses/', include('edu_courses.urls')),
    
    # django auth urls
    path("users/", include("django.contrib.auth.urls")),
    
    # social core django 
    re_path(r'^oauth/', include('social_django.urls', namespace='social')),
    
    # graphql urls 
    path("graphql/", FileUploadGraphQLView.as_view(graphiql=True)),

    
]+ staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
