import logging


from edu_courses.forms import CourseForm
from edu_courses.models import Courses, Category
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from edu_user.models import Enrollment


# for channels
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from edu_courses.consumers import CourseNotificationConsumer


logger = logging.getLogger(__name__)


# only admin and course_creater can create course
@method_decorator(permission_required(['edu_courses.add_courses','edu_courses.change_courses',
                    'edu_courses.delete_courses','edu_courses.view_courses',], raise_exception=True), name='dispatch')
@method_decorator(permission_required(['edu_courses.add_category','edu_courses.change_category',
                    'edu_courses.delete_category','edu_courses.view_category',], raise_exception=True), name='dispatch')
class CourseCreateView(LoginRequiredMixin, CreateView):
    model = Courses
    form_class = CourseForm
    template_name = 'courses/create_courses.html'
    success_url = reverse_lazy('course_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()
        context['category'] = Category.objects.all()
        return context
    
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        self.context = {'categories': categories}
        return render(request, self.template_name, self.context)
    
    def form_valid(self, form):
        form.instance.course_creator = self.request.user 
        CourseNotificationConsumer.send_newcourse_notification(
                    f'New course created: {form.instance.title} by {form.instance.course_creator}'
                )
        logger.info(f'"New course created" Title: {form.instance.title}, Courses Creater {form.instance.course_creator}')
        messages.success(self.request, "Course created successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error creating the course.")
        return super().form_invalid(form)


class CourseDetailView(DetailView):
    model = Courses
    template_name = 'courses/course_detail.html' 


class CourseListView(ListView):
        model = Courses
        template_name = 'courses/course_list.html'
        context_object_name = 'courses'
        ordering = ['title']
        paginate_by = 9


class CourseDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'courses/dashboard.html'
    context_object_name = 'enrolled_courses'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        enrolled_courses = Enrollment.objects.filter(student=user).select_related('course')
        context['enrolled_courses'] = enrolled_courses
        return context


# for sending enroll notification to user
def send_enrollment_notification(username,message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
            'course_enrollment',
            {
                'type': 'enrollment_alert',
                'username': username,
                'message': message 
            }
        )


# for enroll in course
@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Courses, pk=course_id)
    try:
        Enrollment.objects.create(student=request.user, course=course)
        username = request.user.username
        message = f"You have enrolled in course: {course.title}"
        # Send notification to the user
        send_enrollment_notification(username, message)
        logger.info(f'User {request.user.username} enrolled in course: {course.title}')
        messages.success(request, f'Successfully enrolled in {course.title}.')
    except Exception as e:
        messages.error(request, f'Already enrolled in {course.title}.')
    return redirect('home')