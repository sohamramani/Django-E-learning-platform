import graphene
import logging
import random


from django.contrib.auth.models import User
from edu_courses.models import Courses, Category
from edu_user.models import UserProfile as Profile
from edu_user.tasks import send_welcome_email
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.fields import DjangoConnectionField
from graphene_file_upload.scalars import Upload


logger = logging.getLogger(__name__)


class UserType(DjangoObjectType):
    class Meta:
        model = User


class ProfileType(DjangoObjectType):
    class Meta:
        model = Profile


class CourseType(DjangoObjectType):
    """
    Represents a course in the platform.
    """
    category = graphene.String(description="The category name of the course.")
    pk = graphene.Int(description="Primary key of the course.")
    image_url = graphene.String(description="URL of the course image.")

    class Meta:
        model = Courses
        interfaces = (relay.Node,)
        fields = ('id', 'title', 'description', 'start_date', 
                    'end_date', 'image', 'category', 'course_creator')
        description = "A course offered on the platform."
        
    def resolve_category(self, info):
        return self.category.name if self.category else None

    def resolve_image_url(self, info):
        if self.image:
            return self.image.url  # This should be the full MinIO URL
        return None


# mutations

# Mutations for User Registration
class RegisterUser(graphene.Mutation):
    """
    Registers a new user and creates a profile.
    """
    user = graphene.Field(UserType)
    profile = graphene.Field(ProfileType)

    class Arguments:
        username = graphene.String(required=True, description="Unique username for the user.")
        password = graphene.String(required=True, description="Password for the user.")
        email = graphene.String(required=True, description="Email address of the user.")
        first_name = graphene.String()
        last_name = graphene.String()
        gender = graphene.String()
        birth_date = graphene.Date()
        country = graphene.String()
        profile_picture = Upload(required=False)
        resume = Upload(required=False)
        mobile_number = graphene.String()
        otp = graphene.String()

    def mutate(self, info, username, password, email,
                            first_name=None,last_name=None, gender=None, 
                            birth_date=None, country=None, profile_picture=None, 
                            mobile_number=None, resume=None, otp=None):
        if not otp:
            otp = "{:06d}".format(random.randint(0, 999999))
        user = User.objects.create_user(username=username, password=password, 
                                        email=email, first_name=first_name, 
                                        last_name=last_name)
        profile = Profile.objects.create(user=user, gender=gender, birth_date=birth_date, 
                                        country=country, profile_picture=profile_picture,
                                        mobile_number=mobile_number, resume=resume, otp=otp)
        user.is_active = False
        send_welcome_email.delay(user.email, user.username)
        print(f"your otp is :  {otp}")
        return RegisterUser(user=user, profile=profile)


# Mutations for User Profile Update
class UpdateUserProfile(graphene.Mutation):
    user = graphene.Field(UserType)
    profile = graphene.Field(ProfileType)

    class Arguments:
        user_id = graphene.Int(required=True)
        first_name = graphene.String()
        last_name = graphene.String()
        email = graphene.String()
        gender = graphene.String()
        birth_date = graphene.Date()
        country = graphene.String()
        profile_picture = Upload(required=False)
        mobile_number = graphene.String()
        resume = Upload(required=False)

    def mutate(self, info, user_id, **kwargs):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise Exception("User not found")
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            raise Exception("Profile not found")

        # Update user fields
        for attr in ['first_name', 'last_name', 'email']:
            if attr in kwargs and kwargs[attr] is not None:
                setattr(user, attr, kwargs[attr])
        user.save()

        # Update profile fields
        for attr in ['gender', 'birth_date', 'country', 'profile_picture', 
                        'mobile_number', 'resume']:
            if attr in kwargs and kwargs[attr] is not None:
                setattr(profile, attr, kwargs[attr])
        profile.save()
        return UpdateUserProfile(user=user, profile=profile)


# Mutations for Course Creation
class CreateCourse(graphene.Mutation):
    course = graphene.Field(CourseType)
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String()
        start_date = graphene.Date()
        end_date = graphene.Date()
        image = Upload(required=False)
        category = graphene.String()
        course_creator = graphene.String()

    @classmethod
    def mutate(cls, root, info, title, description=None, 
                start_date=None, end_date=None, image=None, 
                category=None, course_creator=None):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("You must be logged in to create a course.")
        if not (user.is_superuser or user.groups.filter(name='course_creator').exists()):
            raise Exception("You do not have permission to create courses.")
        if not title:
            raise Exception("Title is required")
        if start_date and end_date and start_date > end_date:
            raise Exception("Start date cannot be after end date")
        course_creator = User.objects.get(pk=course_creator)
        category_instance = Category.objects.get(pk=category)
        course = Courses.objects.create(title=title, description=description,
                                        start_date=start_date, end_date=end_date, image=image,
                                        category=category_instance, course_creator=course_creator)
        course.save()
        logger.info(f'New course created. Title: {course.title}, Course Creator: {course.course_creator}')
        return CreateCourse(course=course)


# Mutations for User Profile Update
class UpdateUserProfile(graphene.Mutation):
    user = graphene.Field(UserType)
    profile = graphene.Field(ProfileType)

    class Arguments:
        user_id = graphene.Int(required=True)
        first_name = graphene.String()
        last_name = graphene.String()
        email = graphene.String()
        gender = graphene.String()
        birth_date = graphene.Date()
        country = graphene.String()
        profile_picture = Upload(required=False)
        mobile_number = graphene.String()
        resume = Upload(required=False)

    def mutate(self, info, user_id, **kwargs):
        user = User.objects.get(pk=user_id)
        profile = Profile.objects.get(user=user)
        # Update user fields
        for attr in ['first_name', 'last_name', 'email']:
            if attr in kwargs and kwargs[attr] is not None:
                setattr(user, attr, kwargs[attr])
        user.save()
        # Update profile fields
        for attr in ['gender', 'birth_date', 'country', 'profile_picture', 
                        'mobile_number', 'resume']:
            if attr in kwargs and kwargs[attr] is not None:
                setattr(profile, attr, kwargs[attr])
        profile.save()
        return UpdateUserProfile(user=user, profile=profile)


# Mutations for Course Update
class UpdateCourse(graphene.Mutation):
    course = graphene.Field(CourseType)

    class Arguments:
        course_id = graphene.Int(required=True)
        title = graphene.String()
        description = graphene.String()
        start_date = graphene.Date()
        end_date = graphene.Date()
        image = Upload(required=False)
        category = graphene.String()

    def mutate(self, info, course_id, **kwargs):
        course = Courses.objects.get(pk=course_id)
        if 'category' in kwargs and kwargs['category']:
            category_instance = Category.objects.get(pk=kwargs['category'])
            kwargs['category'] = category_instance
        for attr in ['title', 'description', 'start_date', 'end_date', 'image', 'category']:
            if attr in kwargs and kwargs[attr] is not None:
                setattr(course, attr, kwargs[attr])
        course.save()
        return UpdateCourse(course=course)

# Query and Mutation classes
class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)
    user_by_id = graphene.Field(UserType, id=graphene.Int())
    course_by_id = graphene.Field(CourseType, id=graphene.Int())
    course = relay.Node.Field(CourseType)
    # Use DjangoConnectionField for advanced querying (pagination, filtering, sorting)
    all_courses = DjangoConnectionField(
        CourseType,
        title=graphene.String(),
        category=graphene.String(),
        order_by=graphene.String()
    )
    
    def resolve_all_users(root, info):
        return User.objects.all()
    
    def resolve_user_by_id(root, info, id):
        return User.objects.get(pk=id)
    
    def resolve_all_courses(root, info, title=None, category=None, 
                            order_by=None, **kwargs):
        qs = Courses.objects.all()
        if title:
            qs = qs.filter(title__icontains=title)
        if category:
            qs = qs.filter(category__name__icontains=category)
        if order_by:
            qs = qs.order_by(order_by)
        return qs
    
    def resolve_course_by_id(root, info, id):
        return Courses.objects.get(pk=id)
    
    register_user = RegisterUser.Field()
    create_course = CreateCourse.Field()


class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    create_course = CreateCourse.Field()
    update_user_profile = UpdateUserProfile.Field()
    update_course = UpdateCourse.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)