import graphene
import random


from django.contrib.auth.models import User
from edu_user.models import UserProfile as Profile
from edu_user.tasks import send_welcome_email
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload


class UserType(DjangoObjectType):
    class Meta:
        model = User

class ProfileType(DjangoObjectType):
    class Meta:
        model = Profile

class RegisterUser(graphene.Mutation):
    user = graphene.Field(UserType)
    profile = graphene.Field(ProfileType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)
        first_name = graphene.String()
        last_name = graphene.String()
        gender = graphene.String()
        birth_date = graphene.Date()
        country = graphene.String()
        profile_picture = Upload(required=False)
        resume = Upload(required=False)
        mobile_number = graphene.String()
        otp = graphene.String()

    def mutate(self, info, username, password, email,first_name=None,last_name=None, gender=None, birth_date=None, country=None, profile_picture=None, mobile_number=None, resume=None, otp=None):
        if not otp:
            otp = "{:06d}".format(random.randint(0, 999999))
        user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        profile = Profile.objects.create(user=user, gender=gender, birth_date=birth_date, country=country, profile_picture=profile_picture, mobile_number=mobile_number, resume=resume, otp=otp)
        user.is_active = False
        send_welcome_email.delay(user.email, user.username)
        print(f"your otp is :  {otp}")
        return RegisterUser(user=user, profile=profile)

class Query(graphene.ObjectType):
    register_user = RegisterUser.Field()

class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)