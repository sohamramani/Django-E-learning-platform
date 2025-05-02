from django.shortcuts import render, redirect
from django.contrib.auth import login, logout,get_user_model,authenticate,update_session_auth_hash
from .forms import SignupForm, OTPVerificationForm, CustomPasswordChangeForm
from .models import UserProfile
from django.contrib import messages
from .utils import generate_otp, send_otp_sms
from django.contrib.auth.decorators import login_required
User = get_user_model()

def home(request):
    return render(request, "base/home.html")

def signup_view(request):
    if request.method == 'POST':
        user_form = SignupForm(request.POST, request.FILES)
        
        if user_form.is_valid():
            import pdb; pdb.set_trace()
            username = user_form.cleaned_data["username"]
            first_name = user_form.cleaned_data["first_name"]
            last_name = user_form.cleaned_data["last_name"]
            email = user_form.cleaned_data["email"]
            password = user_form.cleaned_data["password"]
            gender = user_form.cleaned_data["gender"]
            birth_date = user_form.cleaned_data["birth_date"]
            country = user_form.cleaned_data["country"]
            mobile_number = request.POST.get('mobile_number')
            profile_picture = request.FILES['profile_picture']
            resume = request.FILES['resume']

            user = User.objects.create_user(username=username, first_name=first_name, 
                                            last_name=last_name, email=email, password=password)
            userprofile = UserProfile.objects.create(user=user, gender=gender, birth_date=birth_date, 
                                                    country=country, profile_picture=profile_picture, 
                                                mobile_number=mobile_number, resume=resume)
            request.user.is_active = False
            otp = generate_otp()
            request.session['otp'] = otp
            send_otp_sms(mobile_number, otp)
            userprofile.save()
            messages.success(request, "Registration successful! Now verify otp for login")
            return redirect('verify_otp')
        else:
            for error in user_form.errors.values():
                    messages.error(request, error)
    else:
        user_form = SignupForm()
    return render(request, 'auth/signup.html', {'user_form': user_form})

def verify_otp(request):
        if request.method == 'POST':
            form = OTPVerificationForm(request.POST)
            if form.is_valid():
                entered_otp = form.cleaned_data['otp']
                stored_otp = request.session.get('otp')
                if entered_otp == stored_otp:
                    request.user.is_active = True
                    del request.session['otp']
                    messages.success(request, "OTP verification successful!")
                    return redirect('home')
                else:
                    messages.error(request, 'Invalid OTP.')
                    return render(request, 'auth/verify_otp.html', {'form': form, 'error': 'Invalid OTP'})
        else:
            form = OTPVerificationForm()
        return render(request, 'auth/verify_otp.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'auth/login.html', {'error': 'Invalid username or password'})
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return render(request, 'base/home.html')

def profile_view(request):
    if request.user.is_authenticated:
        user = request.user
        userprofile = UserProfile.objects.get(user=user)
        context = {
            'user': user,
            'userprofile': userprofile,
        }
        return render(request, 'auth/profile.html', context)
    else:
        return redirect('login_view')
    
@login_required
def change_password(request):
        if request.method == 'POST':
            form = CustomPasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid old password or new password.')
                return render(request, 'auth/change_password.html', {'error': 'Invalid old password or new password'})
        else:
            form = CustomPasswordChangeForm(request.user)
        return render(request, 'auth/change_password.html', {'form': form})