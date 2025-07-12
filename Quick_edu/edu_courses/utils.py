from edu_courses.models import Courses, Category
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from edu_user.models import Enrollment
from edu_user.models import UserProfile
from edu_user.views import User
from faker import Faker


# only for admin that can generate random courses
def random_course_creation():
    fake = Faker()
    title = fake.sentence()  
    description = fake.paragraph(nb_sentences=5)
    category = Category.objects.order_by('?').first()  
    course_creator = User.objects.order_by('?').first()
    courses = Courses.objects.create(title=title, description=description, 
                                            category=category, 
                                            course_creator=course_creator)
    return courses


# only for admin that can generate random courses
@staff_member_required
def random_courses(request):
    count = 0
    for _ in range(100): 
        user = random_course_creation()
        count += 1
    print(f"course count: {count}")
    messages.success(request, f'Successfully {count} random Courses Created.')
    return redirect('home')


# only for admin that can generate random Enrollment
def random_enroll_creation():
    fake = Faker()
    
    while True:
        course = Courses.objects.order_by('?').first()
        student = User.objects.order_by('?').first()
        if not Enrollment.objects.filter(student=student).exists():
            return Enrollment.objects.create(student=student, course=course)


# only for admin that can generate random Enrollment
@staff_member_required
def random_enrolls(request):
    count = 0
    for _ in range(3): 
        user = random_enroll_creation()
        count += 1
    print(f"enroll count: {count}")
    messages.success(request, f'Successfully {count} random student enrolled')
    return redirect('home')


# only for admin that can generate random users
def random_user_creation():
    fake = Faker()
    while True:
        username = fake.user_name()
        if not User.objects.filter(username=username).exists():
            break
    while True:  
        email = fake.email()
        if not User.objects.filter(email=email).exists():
            break
    password = fake.password()
    while True:  
        mobile_number = fake.phone_number()
        if not UserProfile.objects.filter(mobile_number=mobile_number).exists():
            break
    
    user = User.objects.create_user(username=username, email=email, password=password)
    userprofile = UserProfile.objects.create(user=user, mobile_number=mobile_number)
    return userprofile


# only for admin that can generate random users
@staff_member_required
def random_user(request):
    count = 0
    for _ in range(50):
        user = random_user_creation()
        count += 1
    print(f"user count: {count}")
    messages.success(request, f'Successfully {count} random user created')
    return redirect('home')