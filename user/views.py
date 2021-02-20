from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password
from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import Q

from response_management.EMS import *

from user.models import UserProfile
from user.serializers import UserProfileSerializer


class Register(APIView):
    """Register user with username and password"""

    def post(self, request):

        request_json = {
            "username": request.data.get('username'),
            "password": make_password(request.data.get('password'))
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
                    'data': ''
                }

                return Response(response_json, status=403)

        else:
            response_json = {
                'status': False,
                'message': 'Auth Credentials are not provided',
                'data': ''
            }

            return Response(response_json, status=401)




