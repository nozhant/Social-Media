import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password
from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import Q

from response_management.EMS import *

from user.models import UserProfile, Otp
from user.serializers import UserProfileSerializer, OtpSerializer


def generate_otp():
    return str(uuid.uuid4().int)[:5]


class Register(APIView):
    """Register user with username and password and confirm email or phone number by otp that sent to user"""

    def get(self, request):
        """send otp to user email or phone number for confirmation"""

        email_phone = request.GET.get('email_phone')

        request_json = {
            'email_phone': email_phone,
            'code': generate_otp()
        }

        otp_serialized = OtpSerializer(data=request_json)
        if not otp_serialized.is_valid():
            return validate_error(otp_serialized)
        otp_serialized.save()

        # send otp via email or sms

        response_json = {
            'status': True,
            'message': 'otp successfully sent to user',
            'data': {}
        }

        return Response(response_json, status=200)

    def post(self, request):
        """Register user with username and password"""

        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')

        # check that otp is correct or not (otp should match with email or phone number
        otp_obj = Otp.objects.filter(Q(email_phone=email) | Q(email_phone=phone_number) & Q(code=otp)).first()
        if not otp_obj:

            response_json = {
                'status': False,
                'message': 'otp is incorrect',
                'data': {}
            }

            return Response(response_json, status=400)

        # create new user 
        request_json = {
            "username": request.data.get('username'),
            "password": make_password(request.data.get('password')),
            "email": email,
            "phone_number": phone_number
        }

        user_serialized = UserProfileSerializer(data=request_json)
        if not user_serialized.is_valid():
            return validate_error(user_serialized)
        user_serialized.save()

        user_obj = UserProfile.objects.filter(id=user_serialized.data.get('id')).first()
        if not user_obj:
            return existence_error('user')

        token, created = Token.objects.get_or_create(user=user_obj)

        response_json = {
            'status': True,
            'message': 'User successfully registered',
            'data': 'Token {}'.format(token.key)
        }

        return Response(response_json, status=201)


class Login(APIView):
    """Login user with email or username"""

    def post(self, request):

        # get username or email from user
        if request.data.get('username') or request.data.get('email'):
            user_obj = UserProfile.objects.filter(Q(username=request.data.get('username')), Q(email=request.data.get('email'))).first()
            if not user_obj:
                return existence_error('user')

            # check password is correct or not
            if user_obj.check_password(request.data.get('password')):

                token, created = Token.objects.get_or_create(user=user_obj)

                response_json = {
                    'status': True,
                    'message': 'User successfully Logged in',
                    'data': 'Token {}'.format(token.key)
                }

                return Response(response_json, status=200)

            else:

                response_json = {
                    'status': False,
                    'message': 'Permission Denied. The password is wrong',
                    'data': {}
                }

                return Response(response_json, status=403)

        else:
            response_json = {
                'status': False,
                'message': 'Auth Credentials are not provided',
                'data': {}
            }

            return Response(response_json, status=401)


