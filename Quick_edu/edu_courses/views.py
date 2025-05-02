from django.shortcuts import render, redirect, get_object_or_404
from .forms import CourseForm
from .models import Courses, Category
from edu_user.views import User, home
from django.contrib.auth.decorators import login_required
from edu_user.models import Enrollment
from django.contrib import messages


def create_course(request):
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request=request)
        if form.is_valid():
            import pdb; pdb.set_trace()
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]
            image = request.FILES['image']
            category = form.cleaned_data["category"]
            course_creator = form.cleaned_data["course_creator"]
            if title != "" or category != "" or course_creator != "" :
                courses = Courses.objects.create(title=title, description=description, 
                                            start_date=start_date, end_date=end_date, 
                                            image=image, category=category, 
                                            course_creator=course_creator)
                courses.save()
                messages.success(request, f'Successfully Create Course.')
                return redirect('home')
            else:
                messages.error(request,"Title, Category and Course Creator fields are required")
                return render(request, 'courses/create_courses.html',{'form': form} )
    else:
        form = CourseForm(request=request)
    return render(request, 'courses/create_courses.html', {'form': form})

def course_list(request):
    courses = Courses.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})

def course_detail(request, course_id):
        course = get_object_or_404(Courses, id=course_id)
        context = {'course': course}
        return render(request, 'courses/course_detail.html', context)

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Courses, pk=course_id)
    try:
        Enrollment.objects.create(student=request.user, course=course)
        messages.success(request, f'Successfully enrolled in {course.title}.')
    except Exception as e:
        messages.error(request, f'Already enrolled in {course.title}.')
    return redirect('course_detail', course_id=course_id)