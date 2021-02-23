import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import Q

from response_management.EMS import *

from user.models import UserProfile, Otp
from user.serializers import UserProfileSerializer, OtpSerializer, UserProfileShowSerializer, UserProfileGetSerializer, EditUserProfileSerializer
from post.models import Post


def generate_otp():
    return str(uuid.uuid4().int)[:5]


class Register(APIView):
    """Register user with username and password and confirm email or phone number by otp that sent to user"""

    def get(self, request):
        """send otp to user email or phone number for confirmation"""

        email_phone = request.GET.get('email_phone')
        if email_phone is None:
            return unsuccessful_response(message='set phone or email into query param!', status=200)

        # todo: split phone or email and send otp

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
            user_obj = UserProfile.objects.filter(Q(username=request.data.get('username')) |
                                                  Q(email=request.data.get('email'))).first()
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


class Profile(APIView):
    """Allow user to see and edit their profile"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        user_id = request.GET.get('user_id')

        if user_id:
            user_obj = UserProfile.objects.filter(id=user_id).first()
        else:
            user_obj = UserProfile.objects.filter(id=request.user.id).first()
        if not user_obj:
            return existence_error('user')

        user_serialized = UserProfileGetSerializer(user_obj)

        followings = user_serialized.data.get('following')
        followers = user_serialized.data.get('follower')
        if not followings:
            followings_num = 0
        else:
            followings_num = len(followings)

        if not followers:
            followers_num = 0
        else:
            followers_num = len(followers)

        posts_num = Post.objects.filter(user=request.user.id).count()

        response_json = {
            'status': True,
            'message': 'successful',
            'data': {
                'user': user_serialized.data,
                'followings': followings_num,
                'followers': followers_num,
                'posts': posts_num
            }
        }

        return Response(response_json, status=200)

    def post(self, request):
        """Allow user to update their profile info"""

        user_obj = UserProfile.objects.filter(id=request.user.id).first()
        if not user_obj:
            return existence_error('user')

        request_json = {
            'username': request.data.get('username'),
            'name': request.data.get('name'),
            'last_name': request.data.get('last_name'),
            'bio': request.data.get('bio'),
            'website': request.data.get('website'),
            'email': request.data.get('email'),
            'phone_number': request.data.get('phone_number')
        }

        user_serialized = EditUserProfileSerializer(user_obj, data=request_json, partial=True)
        if not user_serialized.is_valid():
            return validate_error(user_serialized)
        user_serialized.save()

        response_json = {
            'status': True,
            'message': 'successful',
            'data': {}
        }

        return Response(response_json, status=201)

    def patch(self, request):
        """Allow user to update their profile photo"""

        user_obj = UserProfile.objects.filter(id=request.user.id).first()
        if not user_obj:
            return existence_error('user')

        request_json = {
            'profile_photo': request.data.get('profile_photo')
        }

        user_serialized = EditUserProfileSerializer(user_obj, data=request_json, partial=True)
        if not user_serialized.is_valid():
            return validate_error(user_serialized)
        user_serialized.save()

        response_json = {
            'status': True,
            'message': 'successful',
            'data': {}
        }

        return Response(response_json, status=201)


class ChangePassword(APIView):
    """Allow user to change their password"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        user_obj = UserProfile.objects.filter(id=request.user.id).first()
        if not user_obj:
            return existence_error('user')

        if user_obj.check_password(old_password):

            request_json = {
                'password': new_password
            }

            user_serialized = UserProfileSerializer(user_obj, data=request_json, partial=True)
            if not user_serialized.is_valid():
                return validate_error(user_serialized)
            user_serialized.save()

            response_json = {
                'status': True,
                'message': "The password successfully changed",
                'data': {}
            }

            return Response(response_json, status=200)

        else:
            response_json = {
                'status': False,
                'message': "Password is wrong",
                'data': {}
            }

            return Response(response_json, status=200)


class FollowOrUnfollow(APIView):
    """Follow or unfollow a specific user"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        user_id = request.data.get('user_id')  # user to follow or unfollow
        follow = request.data.get('follow')  # true for follow and false for unfollow

        if follow:
            # add requested user to user id's followers
            user_follower_obj = UserProfile.objects.filter(id=user_id).first()
            if not user_follower_obj:
                return existence_error('user')
            user_follower_serialized = UserProfileSerializer(user_follower_obj)
            # user id followers
            user_followers = user_follower_serialized.data.get('follower')

            user_followers.append(request.user.id)

            follower_json = {
                'follower': user_followers
            }

            user_follower_serialized = UserProfileSerializer(user_follower_obj, data=follower_json, partial=True)
            if not user_follower_serialized.is_valid():
                return validate_error(user_follower_serialized)
            user_follower_serialized.save()

            # add user id to requested user's following
            user_following_obj = UserProfile.objects.filter(id=request.user.id).first()
            if not user_following_obj:
                return existence_error('user')

            user_following_serialized = UserProfileSerializer(user_following_obj)
            # requested user followings
            user_followings = user_following_serialized.data.get('following')

            user_followings.append(user_id)

            following_json = {
                'following': user_followings
            }

            user_following_serialized = UserProfileSerializer(user_following_obj, data=following_json, partial=True)
            if not user_following_serialized.is_valid():
                return validate_error(user_following_serialized)
            user_following_serialized.save()

            response_json = {
                'status': True,
                'message': "successful",
                'data': {}
            }

            return Response(response_json, status=200)

        if not follow:
            # remove requested user from user id's followers
            user_follower_obj = UserProfile.objects.filter(id=user_id).first()
            if not user_follower_obj:
                return existence_error('user')
            user_follower_serialized = UserProfileSerializer(user_follower_obj)
            # user id followers
            user_followers = user_follower_serialized.data.get('follower')

            user_followers.remove(request.user.id)

            follow_json = {
                'follower': user_followers
            }

            user_follower_serialized = UserProfileSerializer(user_follower_obj, data=follow_json, partial=True)
            if not user_follower_serialized.is_valid():
                return validate_error(user_follower_serialized)
            user_follower_serialized.save()

            # remove user id to requested user's following
            user_following_obj = UserProfile.objects.filter(id=request.user.id).first()
            if not user_following_obj:
                return existence_error('user')

            user_following_serialized = UserProfileSerializer(user_following_obj)
            # requested user followings
            user_followings = user_following_serialized.data.get('following')

            user_followings.remove(user_id)

            following_json = {
                'following': user_followings
            }

            user_following_serialized = UserProfileSerializer(user_following_obj, data=following_json, partial=True)
            if not user_following_serialized.is_valid():
                return validate_error(user_following_serialized)
            user_following_serialized.save()

            response_json = {
                'status': True,
                'message': "successful",
                'data': {}
            }

            return Response(response_json, status=200)
















