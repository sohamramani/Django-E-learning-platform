import datetime
import re


from django.contrib.auth.models import User, Group
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test import TestCase
from django.test import TestCase, Client as DjangoClient
from django.urls import reverse
from edu_courses.models import Courses, Category
from edu_courses.models import Courses, Category 
from edu_user.models import Enrollment
from edu_user.models import UserProfile as Profile
from edu_user.tasks import send_reset_password_email_task
from graphene.test import Client
from Quick_edu.schema import schema
from unittest import mock


class SchemaTestCase(TestCase):
    def setUp(self):
        self.graphql_client = Client(schema)
        self.django_client = DjangoClient()
        self.user = User.objects.create_user(username='testuser', password='testpass', email='test@example.com')
        self.profile = Profile.objects.create(user=self.user, gender='M', country='IN', otp='123456')
        self.category = Category.objects.create(name='Science')
        self.course = Courses.objects.create(
            title='Physics', description='Learn Physics', category=self.category, 
            course_creator=self.user, start_date=datetime.date.today(), end_date=datetime.date.today()
        )
        # Add user to course_creator group for permissions
        group, _ = Group.objects.get_or_create(name='course_creator')
        self.user.groups.add(group)
        self.user.is_superuser = True
        self.user.save()

    def test_register_user_success(self):
        mutation = '''
            mutation RegisterUser($username: String!, $password: String!, $email: String!, $firstName: String!, $lastName: String!, $mobileNumber: String!) {
                registerUser(username: $username, password: $password, email: $email, firstName: $firstName, lastName: $lastName, mobileNumber: $mobileNumber) {
                    user { username email firstName lastName }
                    profile { country }
                }
            }
        '''
        variables = {
            'username': 'newuser',
            'password': 'newpass',
            'email': 'new@example.com',
            'firstName': 'First',
            'lastName': 'Last',
            'mobileNumber': '1234567890'
        }
        executed = self.graphql_client.execute(mutation, variables=variables)
        self.assertIsNone(executed.get('errors'))
        self.assertEqual(executed['data']['registerUser']['user']['username'], 'newuser')
        self.assertEqual(executed['data']['registerUser']['user']['firstName'], 'First')
        self.assertEqual(executed['data']['registerUser']['user']['lastName'], 'Last')

    def test_register_user_missing_required(self):
        mutation = '''
            mutation {
                registerUser(password: "pass", email: "mail@example.com") {
                    user { username }
                }
            }
        '''
        executed = self.graphql_client.execute(mutation)
        self.assertIsNotNone(executed.get('errors'))

    def test_update_user_profile_success(self):
        mutation = '''
            mutation {
                updateUserProfile(userId: %d, firstName: "Updated", country: "US") {
                    user { firstName }
                    profile { country }
                }
            }
        ''' % self.user.id
        executed = self.graphql_client.execute(mutation)
        self.assertIsNone(executed.get('errors'))
        self.assertEqual(executed['data']['updateUserProfile']['user']['firstName'], 'Updated')
        self.assertEqual(executed['data']['updateUserProfile']['profile']['country'], 'US')

    def test_update_user_profile_user_not_found(self):
        mutation = '''
            mutation {
                updateUserProfile(userId: 99999, firstName: "NoUser") {
                    user { firstName }
                }
            }
        '''
        executed = self.graphql_client.execute(mutation)
        self.assertIsNotNone(executed.get('errors'))
        self.assertIn('does not exist', executed['errors'][0]['message'])
        
    def test_create_course_success(self):
        # Simulate authenticated user in context
        context = mock.Mock()
        context.user = self.user
        mutation = '''
            mutation CreateCourse($title: String!, $category: String!, $courseCreator: String!) {
                createCourse(title: $title, category: $category, courseCreator: $courseCreator) {
                    course { title category }
                }
            }
        '''
        variables = {
            'title': 'Chemistry',
            'category': str(self.category.pk),
            'courseCreator': str(self.user.pk)
        }
        executed = self.graphql_client.execute(mutation, variables=variables, context_value=context)
        self.assertIsNone(executed.get('errors'))
        self.assertEqual(executed['data']['createCourse']['course']['title'], 'Chemistry')

    def test_create_course_permission_denied(self):
        self.user.groups.clear()
        self.user.is_superuser = False
        self.user.save()
        context = mock.Mock()
        context.user = self.user
        mutation = '''
            mutation {
                createCourse(title: "NoPerm", category: "%d", courseCreator: "%d") {
                    course { title }
                }
            }
        ''' % (self.category.pk, self.user.pk)
        executed = self.graphql_client.execute(mutation, context_value=context)
        self.assertIsNotNone(executed.get('errors'))
        self.assertIn('permission', executed['errors'][0]['message'])


    def test_update_course_success(self):
        mutation = '''
            mutation {
                updateCourse(courseId: %d, title: "UpdatedTitle") {
                    course { title }
                }
            }
        ''' % self.course.id
        executed = self.graphql_client.execute(mutation)
        self.assertIsNone(executed.get('errors'))
        self.assertEqual(executed['data']['updateCourse']['course']['title'], 'UpdatedTitle')

    def test_update_course_not_found(self):
        mutation = '''
            mutation {
                updateCourse(courseId: 9999, title: "NoCourse") {
                    course { title }
                }
            }
        '''
        executed = self.graphql_client.execute(mutation)
        self.assertIsNotNone(executed.get('errors'))

    def test_query_all_users(self):
        query = '''
            query {
                allUsers { username }
            }
        '''
        executed = self.graphql_client.execute(query)
        self.assertIsNone(executed.get('errors'))
        self.assertTrue(any(u['username'] == 'testuser' for u in executed['data']['allUsers']))




# class PasswordResetTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', email='test@example.com', password='oldpassword')

#     def test_forgot_password_email_sent(self):
#             # Simulate the forgot password request
            
#             send_reset_password_email_task.delay(self.user.pk, self.user.email)
#             # Assert that an email was sent
#             self.assertEqual(len(mail.outbox), 1)
#             sent_email = mail.outbox[0]
#             # Assert email content (customize as needed)
#             self.assertEqual(sent_email.subject, 'Password reset request')
#             self.assertEqual(sent_email.to, ['test@example.com'])
#             self.assertIn('reset', sent_email.body) # Check for

        # # 2. Extract the reset link
        # email_content = mail.outbox[0].body
        # uid_token_regex = r"reset/([0-9A-Za-z_\-]+)/([0-9A-Za-z_\-]+)/"
        # match = re.search(uid_token_regex, email_content)
        # self.assertIsNotNone(match, "UID and token not found in email")
        # uidb64, token = match.groups()
        # reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})

        # # 3. Verify the reset link
        # response = self.client.get(reset_url)
        # self.assertEqual(response.status_code, 200)

        # # 4. Set a new password
        # response = self.client.post(reset_url, {'new_password1': 'newpassword', 'new_password2': 'newpassword'})
        # self.assertEqual(response.status_code, 302)

        # # 5. Verify password change
        # self.assertTrue(self.client.login(username='testuser', password='newpassword'))


# class EnrollmentTest(TestCase):
#     def setUp(self):
#         # Create test data (courses, students)
#         self.course_creator = User.objects.create(username="John Doe", password="Password@123")
#         self.category = Category.objects.create(name="Programming", description="Courses related to programming languages")
#         self.student1 = User.objects.create_user(username='student1', password='password')
#         self.student2 = User.objects.create_user(username='student2', password='password')
#         self.course1 = Courses.objects.create(
#                 title="Introduction to Python",
#                 description="A beginner-friendly Python course",
#                 start_date="2023-01-01",
#                 end_date="2023-12-31",
#                 image="Quick_edu/media/course_image/certificate.jpg",
#                 course_creator=self.course_creator,
#                 category=self.category,
#             )
#         self.course2 = Courses.objects.create(
#                 title='Course 2',
#                 description="A course2 of Python course",
#                 start_date="2023-01-02",
#                 end_date="2023-12-20",
#                 image="Quick_edu/media/course_image/certificate.jpg",
#                 course_creator=self.course_creator,
#                 category=self.category,
#         )

#     def test_successful_enrollment(self):
#         # Enroll student1 in course1
#         enrollment = Enrollment.objects.create(student=self.student1, course=self.course1)

#         # Assertions
#         self.assertEqual(enrollment.student, self.student1)
#         self.assertEqual(enrollment.course, self.course1)

#     def test_duplicate_enrollment(self):
#         # Enroll student1 in course1
#         Enrollment.objects.create(student=self.student1, course=self.course1)

#         # Attempt to enroll student1 in course1 again
#         with self.assertRaises(ValidationError):
#             Enrollment.objects.create(student=self.student1, course=self.course1)

# class CourseModelTest(TestCase):
#         def setUp(self):
#             self.course_creator = User.objects.create(username="John Doe", password="Password@123")
#             self.category = Category.objects.create(name="Programming", description="Courses related to programming languages")
#             self.course = Courses.objects.create(
#                 title="Introduction to Python",
#                 description="A beginner-friendly Python course",
#                 start_date="2023-01-01",
#                 end_date="2023-12-31",
#                 image="Quick_edu/media/course_image/certificate.jpg",
#                 course_creator=self.course_creator,
#                 category=self.category,
#             )
#             self.group = Group.objects.create(name="Instructors")
#         def test_add_permission_to_group_and_user(self):
#             content_type = ContentType.objects.get_for_model(User)
#             permission = Permission.objects.create(
#                 codename='can_create_course',
#                 name='Can create course',
#                 content_type=content_type,
#             )
#             self.group.permissions.add(permission)
#             self.course_creator.groups.add(self.group)
#             self.assertTrue(self.course_creator.has_perm('auth.can_create_course'))


#         def test_course_creation(self):
#             self.assertEqual(self.course.title, "Introduction to Python")
#             self.assertEqual(self.course.description, "A beginner-friendly Python course")
#             self.assertEqual(self.course.start_date, "2023-01-01")
#             self.assertEqual(self.course.end_date, "2023-12-31")
#             self.assertEqual(self.course.image, "Quick_edu/media/course_image/certificate.jpg")
#             self.assertEqual(self.course.course_creator, self.course_creator)
#             self.assertEqual(self.course.category, self.category)

#         def test_course_relationship_with_course_creator(self):
#             self.assertEqual(self.course.course_creator.username, "John Doe")   
# from django.test import Client

# class CourseCreationPermissionTest(TestCase):
#     def setUp(self):
#         self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
#         self.instructor_user = User.objects.create_user('instructor', 'instructor@example.com', 'password')
#         self.regular_user = User.objects.create_user('user', 'user@example.com', 'password')
#         self.group = Group.objects.create(name="Instructors")
#         self.instructor_user.is_staff = True
#         self.client = Client()
#         self.client.login(username='admin', password='password')
#         self.client.login(username='instructor', password='password')
#         self.client.login(username='user', password='password')
#         self.category = Category.objects.create(name="Programming", description="Courses related to programming languages")
#         self.course = Courses.objects.create(
#             title="Introduction to Python",
#             description="A beginner-friendly Python course",
#             start_date="2023-01-01",
#             end_date="2023-12-31",
#             image="Quick_edu/media/course_image/certificate.jpg",
#             course_creator=self.instructor_user,
#             category=self.category,
#         )
        # content_type = ContentType.objects.get_for_model(User)
        # self.can_add = Permission.objects.create(codename='add_courses',name='Can add courses',content_type=content_type)
        # self.can_view = Permission.objects.create(codename='view_courses',name='Can view courses',content_type=content_type)
        # self.can_delete = Permission.objects.create(codename='delete_courses',name='Can delete courses',content_type=content_type)
        # self.can_change = Permission.objects.create(codename='change_courses',name='Can change courses',content_type=content_type)
        
        # self.group.permissions.add(self.can_add,self.can_view,self.can_delete,self.can_change)
        # self.instructor_user.groups.add(self.group)
        # self.instructor_user.user_permissions.add(self.can_add,self.can_view,self.can_delete,self.can_change)
        # self.instructor_user.save()
    # def test_add_permission_to_group_and_user(self):
    #         content_type = ContentType.objects.get_for_model(User)
    #         permission = Permission.objects.create(
    #             codename='can_create_course',
    #             name='Can create course',
    #             content_type=content_type,
    #         )
    #         self.group.permissions.add(permission)
    #         self.instructor_user.groups.add(self.group)
    #         self.assertTrue(self.instructor_user.has_perm('auth.can_create_course'))
        
    # def test_admin_can_create_course(self):
    #     self.client.login(username='admin', password='password')
    #     response = self.client.post(reverse('create_courses'), {
    #         'title': 'Advanced Python',
    #         'description': 'An advanced course on Python programming',
    #         'start_date': '2023-02-01',
    #         'end_date': '2023-12-31',
    #         'image': 'Quick_edu/media/course_image/certificate.jpg',
    #         'course_creator': self.admin_user.id,
    #         'category': self.category.id,
    #     })
    #     self.assertEqual(response.status_code, 302)
    #     self.assertTrue(Courses.objects.filter(title='Advanced Python').exists())
        
    # def test_instructor_can_create_course(self):
    #     self.client.login(username='instructor', password='password')
    #     response = self.client.post(reverse('create_courses'), {
    #         'title': 'Advanced Python',
    #         'description': 'An advanced course on Python programming',
    #         'start_date': '2023-02-01',
    #         'end_date': '2023-12-31',
    #         'image': 'Quick_edu/media/course_image/certificate.jpg',
    #         'course_creator': self.instructor_user.id,
    #         'category': self.category.id,
    #     })
    #     self.assertEqual(response.status_code, 302)
    #     self.assertTrue(Courses.objects.filter(title='Advanced Python').exists())
    
    # def test_regular_user_cannot_create_course(self):
    #     self.client.login(username='user', password='password')
    #     response = self.client.post(reverse('create_courses'), {
    #         'title': 'Advanced Python',
    #         'description': 'An advanced course on Python programming',
    #         'start_date': '2023-02-01',
    #         'end_date': '2023-12-31',
    #         'image': 'Quick_edu/media/course_image/certificate.jpg',
    #         'course_creator': self.regular_user.id,
    #         'category': self.category.id,
    #     })
    #     self.assertEqual(response.status_code, 403)
    #     self.assertFalse(Courses.objects.filter(title='Advanced Python').exists())
    
    # def test_course_list_view(self):
    #     response = self.client.get(reverse('course_list'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'courses/course_list.html')
    #     self.assertContains(response, "Introduction to Python")
    #     self.assertContains(response, "A beginner-friendly Python course")
    
    # def test_course_detail_view(self):
    #     response = self.client.get(reverse('course_detail', args=[self.course.id]))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'courses/course_detail.html')
    #     self.assertContains(response, "Introduction to Python")
    #     self.assertContains(response, "A beginner-friendly Python course")

