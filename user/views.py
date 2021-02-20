from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password

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

