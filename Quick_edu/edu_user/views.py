import json
import logging
import paypalrestsdk
import random
import razorpay
import re
import requests


from edu_user.forms import (
    SignupForm, 
    OTPVerificationForm, 
    PasswordResetRequestForm,
    )
from edu_user.models import UserProfile,Order
from edu_user.tasks import (
    send_reset_password_email_task, 
    send_welcome_email,
    send_become_an_instructor_email,
    )
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django_countries.fields import CountryField
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.http import  urlsafe_base64_decode
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from edu_courses.tasks import export_course_excel,export_student_excel
from edu_user.credentials import PAYPAL_SECRET, PAYPAL_CLIENT_ID
from edu_user.models import Order
from edu_user.tokens import account_activation_token
from edu_user.utils import PaymentStatus, MessageHandler # MessageHandler use for twillow but can not use now


paypalrestsdk.configure({
    "mode": "sandbox", 
    "client_id": PAYPAL_CLIENT_ID,
    "client_secret": PAYPAL_SECRET,
})


logger = logging.getLogger(__name__)
User = get_user_model()

# for api signup
def signupapi(request):
    country_choices = CountryField().choices
    return render(request, 'auth/signupapi.html', {'country': country_choices})


def home(request):
    return render(request, "base/home.html")


class SignUpView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = SignupForm()
        return render(request, 'auth/signup.html', {'form': form})
    
    def post(self, request):
        form = SignupForm(request.POST,request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            gender = form.cleaned_data["gender"]
            birth_date = form.cleaned_data["birth_date"]
            country = form.cleaned_data["country"]
            mobile_number = form.cleaned_data['mobile_number']
            profile_picture = request.FILES.get('profile_picture', None)
            resume = request.FILES.get('resume', None)
            otp = random.randint(100000, 999999)
            # convert mobile number for sending sms
            code = str(mobile_number.country_code)
            phone = str(mobile_number.national_number)
            phone_number = "+"+code+ " " +phone
            
            userprofile = UserProfile.objects.update_or_create(user=user, gender=gender, 
                                                birth_date=birth_date, country=country, 
                                                profile_picture=profile_picture, mobile_number=phone_number, 
                                                resume=resume, otp=otp)
                        
            current_site = get_current_site(request)
            # message_handler = MessageHandler(phone_number, otp).send_otp_on_phone()
            send_welcome_email.delay(user.email, user.username)
            logger.info(f"your otp is :  {otp}")
            messages.success(request, "Registration successful! Now verify otp for login")
            return redirect('verify_otp', user_id=user.id)
        else:
            for error in form.errors.values():
                messages.error(request, error)
        return render(request, 'auth/signup.html', {'form': form})


# OTP verification
def verify_otp(request, user_id):
        user = User.objects.get(id=user_id)
        if request.method == 'POST':
            form = OTPVerificationForm(request.POST)
            if form.is_valid():
                entered_otp = form.cleaned_data['otp']
                stored_otp = user.userprofile.otp
                if entered_otp == stored_otp:
                    user.is_active = True
                    user.save()
                    logger.info(f"User {user.username} verified OTP successfully.")
                    messages.success(request, "OTP verification successful! now you can login")
                    return redirect('home')
                else:
                    messages.error(request, 'Invalid OTP.')
                    return render(request, 'auth/verify_otp.html', {'form': form, 'error': 'Invalid OTP'})
        else:
            form = OTPVerificationForm()
        return render(request, 'auth/verify_otp.html', {'form': form})


#  user login
def login_user(request):
    if request.user.is_authenticated:
            return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'auth/login.html', {'error': 'Invalid username or password'})
    return render(request, 'auth/login.html')


# user logout
def logout_user(request):
    logout(request)
    return redirect('home')


# user profile
def profile(request):
    if request.user.is_authenticated:
        user = request.user
        userprofile = UserProfile.objects.get(user=user)
        country_choices = userprofile._meta.get_field('country').choices
        gender_choices = userprofile._meta.get_field('gender').choices
        context = {     
            'user': user,
            'userprofile': userprofile,
            'country_choices': country_choices,
            'gender_choices': gender_choices,
        }
        return render(request, 'auth/profile.html', context)
    else:
        return redirect('login')


# for requesting password reset
def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                userpk = user.pk
                send_reset_password_email_task.delay(userpk, email)
                messages.success(request, "password reset email has been sent.")
                return render(request, 'base/home.html')
            except User.DoesNotExist:
                user = None
                messages.error(request, "user not found!")
                return render(request, 'auth/password_reset_form.html')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'auth/password_reset_form.html', {'form': form})


# for password reset confirm
def password_reset_confirm(request, uidb64, token):
    if request.method == 'POST':
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
                new_password1 = request.POST.get('new_password1')
                new_password2 = request.POST.get('new_password2')
                password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
                user = User.objects.get(pk=uid)
                if new_password1 == new_password2:
                    if re.fullmatch(password_pattern, new_password1):
                        user.set_password(new_password1)
                        user.save()
                        messages.success(request, 'Password changed successfully.')
                        return render(request, 'auth/login.html')
                    else:
                        messages.error(request, 'Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number and one special character.')
                        return render(request, 'auth/password_reset_confirm.html', {'uid': uid, 'token': token})
                else:
                    messages.error(request, 'New password and confirm password do not match.')
                    return render(request, 'auth/login.html')
        else:
            messages.error(request, 'Activation link is invalid!')
            return redirect('password_reset_confirm')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'auth/password_reset_confirm.html', {'form': form})


# for sending email to admin for reports
class Reports(View):
    def get(self, request, action=None):
        if action == 'student_report':
            return self.student_report(request)
        elif action == 'course_report':
            return self.course_report(request)
        else:
            return TemplateResponse(request, 'auth/reports.html')
        
    def student_report(self, request):
        admin_email = 'sohamramani20@gmail.com'
        export_student_excel.delay(admin_email)
        messages.success(request, 'Student Report email sent!... Check Your Inbox')
        return TemplateResponse(request, 'auth/reports.html')
    
    def course_report(self,request):
        admin_email = 'sohamramani20@gmail.com'
        export_course_excel.delay(admin_email)
        messages.success(request, 'Course Report email sent!... Check Your Inbox')
        return TemplateResponse(request, 'auth/reports.html')


# for send email to admin for become an instructor
def become_an_instructor(request):
    if request.user.is_authenticated: 
        if request.method == 'POST':
            user_email = request.user.email
            admin_email = 'sohamramani20@gmail.com'
            username = request.POST.get('username')
            email = request.POST.get('email')
            try:
                user_email = User.objects.get(email=user_email)
                user = User.objects.get(username=request.user)
                if not username == '' or email == '':
                    send_become_an_instructor_email.delay(admin_email, email, username)
                    logger.info('become instructor email sent successfully.....')
                    messages.success(request, 'Email sent successfully , please wait for reply from admin')
                    return redirect('home')
                else:
                    messages.error(request, 'Please fill all the fields')
                    return redirect('become_an_instructor')
            except User.DoesNotExist:
                return HttpResponse(f"User with email {user_email} or {user} does not exist.")
        else:
            return render(request, 'auth/become_instructor.html')
    else:
        messages.error(request, 'you need to login for become instructor')
        return render(request, 'auth/login.html')



# paypal payment integration
def create_payment(request):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal",
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse('execute_payment')),
            "cancel_url": request.build_absolute_uri(reverse('payment_failed')),
        },
        "transactions": [
            {
                "amount": {
                    "total": "10.00",  # Total amount in USD
                    "currency": "USD",
                },
                "description": "Payment for Product/Service",
            }
        ],
    })

    if payment.create():
        return redirect(payment.links[1].href)  # Redirect to PayPal for payment
    else:
        return render(request, 'paypal/payment_failed.html')

def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        return render(request, 'paypal/payment_success.html')
    else:
        return render(request, 'paypal/payment_failed.html')

def payment_checkout(request):
    return render(request, 'paypal/checkout.html')


def payment_failed(request):
    return render(request, 'paypal/payment_failed.html')


def payment_success(request):
    return render(request, 'paypal/payment_success.html')


# razorpay payment integration
def order_payment(request):
    if request.method == "POST":
        name = request.user.username
        amount = 800 
        
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create(
            {"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"}
        )
        order = Order.objects.create(
            name=name, amount=amount, provider_order_id=razorpay_order["id"]
        )
        order.save()
        return render(
            request,    
            "razorpay/payment.html",
            {
                "callback_url": "http://" + "127.0.0.1:8000" + "/users/callback/",
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "order": order,
            },
        )
    return render(request, "razorpay/payment.html")


@csrf_exempt
def callback(request):
    def verify_signature(response_data):
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        params_dict = {
            'razorpay_order_id': response_data.get('razorpay_order_id'),
            'razorpay_payment_id': response_data.get('razorpay_payment_id'),
            'razorpay_signature': response_data.get('razorpay_signature')
        }
        return client.utility.verify_payment_signature(params_dict)

    if "razorpay_signature" in request.POST:
        
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.signature_id = signature_id
        order.save()
        try:
            verify_signature(request.POST)
            order.status = PaymentStatus.SUCCESS
            order.save()
            return render(request, "razorpay/callback.html", context={"status": order.status})
        except Exception as e:
            order.status = PaymentStatus.FAILURE
            order.save()
            return render(request, "razorpay/callback.html", context={"status": order.status, "error": str(e)})
    else:
        payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
        provider_order_id = json.loads(request.POST.get("error[metadata]")).get(
            "order_id"
        )
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.status = PaymentStatus.FAILURE
        order.save()
        return render(request, "razorpay/callback.html", context={"status": order.status})
    
# Cashfree payment integration
def initiate_cashfree_payment(request):
    total_amount = 800
    order_id = request.POST.get('order_id')
    merchant_id = settings.CASHFREE_APP_ID
    secret_key = settings.CASHFREE_SECRET_KEY
    payment_url = 'https://sandbox.cashfree.com/pg/orders'

    payload = {
        "customer_details": {
            "customer_id": request.user.username,
            'customer_name': request.user.first_name,
            'customer_email': request.user.email,
            'customer_phone': '9999999999',
        },
        "order_meta": {
            "return_url": 'http://127.0.0.1:8000/users/success/',
            "notify_url": 'http://127.0.0.1:8000/users/notify/', 
        },
        'order_id': order_id,  
        'order_amount': str(total_amount),
        'order_currency': 'INR',
        'order_note': 'Payment for Course Enrollment',
    }
    headers = {
    "accept": "application/json",
    "x-api-version": "2022-09-01",
    "content-type": "application/json",
    "x-client-id": merchant_id,
    "x-client-secret": secret_key
}
    response = requests.post(payment_url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        payment_session_id = data['payment_session_id']
        order_id = data['order_id']
        return render(request, 'cashfree/cashfree_payment.html', {'payment_session_id': payment_session_id, 'order_id': order_id })
    else:
        return JsonResponse({'error': 'Failed to initiate payment'})