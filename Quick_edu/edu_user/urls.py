from django import views

from django.urls import path
from edu_user import views
from edu_user.views import Reports
from edu_courses.utils import random_user
from edu_user import utils

urlpatterns = [
    # auth urls
    path("signupapi/", views.signupapi, name="signupapi"), #this is the signup api that handles user registration
    
    path("signup/", views.SignUpView.as_view(), name="signup"), #this is the normal view for signup
    path("login/", views.login_user, name="login"),
    path('verify_otp/<int:user_id>/', views.verify_otp, name='verify_otp'),
    path("profile/", views.profile, name="profile"),
    path("logout/", views.logout_user, name="logout"),
    path('reset-password/', views.password_reset_request, name='password_reset_request'),
    path('reset-password/confirm/<uidb64>/<token>', views.password_reset_confirm, name='reset_password_confirm'),
    path("become-an-instructor/", views.become_an_instructor, name="become_an_instructor"),
    
    # for downlodwing resume 
    path("download/", utils.download_file, name="download_file"),
    
    # reports genration urls
    path('reports/', Reports.as_view(), name='reports'),
    path('reports/<str:action>/', Reports.as_view(), name='student_report'),
    path('reports/<str:action>/', Reports.as_view(), name='course_report'),
    
    # random user creation
    path('random_user/', random_user, name='random_user'),
    
    # payal 
    path('checkout/', views.payment_checkout, name='checkout_payment'),
    path('create_payment/', views.create_payment, name='create_payment'),
    path('execute_payment/', views.execute_payment, name='execute_payment'),
    path('payment_failed', views.payment_failed, name='payment_failed'),
    
    
    # razorpay urls,
    path("payment/", views.order_payment, name="payment"),
    path("callback/", views.callback, name="callback"),
    
    # cashfree payment urls
    path('initiate-payment/', views.initiate_cashfree_payment, name='initiate_payment'),
    path('payment_success/', views.payment_success, name='payment_success'),
]