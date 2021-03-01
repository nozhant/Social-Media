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

from social_media.utils import send_email
from user.models import UserProfile, Otp, UserFollowing, UserFollower
from user.serializers import UserProfileSerializer, OtpSerializer, UserProfileShowSerializer, UserProfileGetSerializer, EditUserProfileSerializer, UserFollowingSerializer, UserFollowerSerializer, UserFollowingShowSerializer, UserFollowerShowSerializer
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

        code = generate_otp()

        request_json = {
            'email_phone': email_phone,
            'code': code
        }

        otp_serialized = OtpSerializer(data=request_json)
        if not otp_serialized.is_valid():
            return validate_error(otp_serialized)
        otp_serialized.save()

        email_body = "Hi there,You're almost set! Verify your email by enter this code: {0}".format(code)
        send_email('Verification Code', email_body, email_phone)

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

        # create following and follower object
        following_obj = UserFollowing.objects.create(user_id=user_obj)
        follower_obj = UserFollower.objects.create(user_id=user_obj)

        token, created = Token.objects.get_or_create(user=user_obj)

        otp_obj.delete()

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
        if request.data.get('username'):
            user_obj = UserProfile.objects.filter(username=request.data.get('username')).first()
        if request.data.get('email'):
            user_obj = UserProfile.objects.filter(email=request.data.get('email')).first()
        if request.data.get('phone_number'):
            user_obj = UserProfile.objects.filter(phone_number=request.data.get('phone_number')).first()
        if not user_obj:
            return existence_error('user')

        # check password is correct or not
        if user_obj.check_password(request.data.get('password')):

            if user_obj.two_step:
                response_json = {
                    'status': True,
                    'message': 'Two step verification is on for user. proceed via two step verification api to login',
                    'data': {}
                }

                return Response(response_json, status=200)

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


class TwoStepVerificationLogin(APIView):
    """Process two step verification to login user"""

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

        response_json = {
            'status': True,
            'message': 'otp successfully sent to user',
            'data': {}
        }

        return Response(response_json, status=200)

    def post(self, request):
        """Login user after two step verification"""

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

        # login user
        user_obj = UserProfile.objects.filter(
            Q(phone_number=request.data.get('phone_number')) | Q(email=request.data.get('email'))).first()

        token, created = Token.objects.get_or_create(user=user_obj)

        response_json = {
            'status': True,
            'message': 'User successfully Logged in',
            'data': 'Token {}'.format(token.key)
        }

        return Response(response_json, status=200)


class Logout(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError,):
            pass

        response_json = {
            'status': True,
            'message': 'successful',
            'data': ''
        }

        return Response(response_json, status=200)


class Profile(APIView):
    """Allow user to see and edit their profile"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        # to get another user profile data
        user_id = request.GET.get('user_id')

        if user_id:
            user_obj = UserProfile.objects.filter(id=user_id).first()
            followings_obj = UserFollowing.objects.filter(user_id=user_id).first()
            followers_obj = UserFollower.objects.filter(user_id=user_id).first()
            posts_num = Post.objects.filter(user=user_id).count()
        else:
            user_obj = UserProfile.objects.filter(id=request.user.id).first()
            followings_obj = UserFollowing.objects.filter(user_id=request.user.id).first()
            followers_obj = UserFollower.objects.filter(user_id=request.user.id).first()
            posts_num = Post.objects.filter(user=request.user.id).count()
        if not user_obj:
            return existence_error('user')

        user_serialized = UserProfileGetSerializer(user_obj)
        user_followings_serialized = UserFollowingSerializer(followings_obj)
        followings_num = len(user_followings_serialized.data.get('following_user_id'))
        user_followers_serialized = UserFollowerSerializer(followers_obj)
        followers_num = len(user_followers_serialized.data.get('follower_user_id'))

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
            'phone_number': request.data.get('phone_number'),
            'business': request.data.get('business'),
            'country': request.data.get('country'),
            'city': request.data.get('city')
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


class GetFollowerOrFollowings(APIView):
    """Allow user to see follower and followings"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """see their own follower and followings"""
        followers = request.GET.get('followers')
        followings = request.GET.get('followings')

        if followers:

            follower_obj = UserFollower.objects.filter(user_id=request.user.id).first()

            follower_serialized = UserFollowerShowSerializer(follower_obj)

            response_json = {
                'status': True,
                'message': 'successful',
                'data': follower_serialized.data
            }

            return Response(response_json, status=200)

        if followings:

            following_obj = UserFollowing.objects.filter(user_id=request.user.id).first()

            following_serialized = UserFollowingShowSerializer(following_obj)

            response_json = {
                'status': True,
                'message': 'successful',
                'data': following_serialized.data
            }

            return Response(response_json, status=200)

        response_json = {
            'status': False,
            'message': 'unsuccessful',
            'data': {}
        }

        return Response(response_json, status=200)

    def post(self, request):
        """see other users follower and following"""

        user_id = request.data.get('user_id')
        followers = request.data.get('followers')
        followings = request.data.get('followings')

        if followers:
            follower_objs = UserFollower.objects.filter(user_id=user_id)

            follower_serialized = UserFollowerSerializer(follower_objs, many=True)

            response_json = {
                'status': True,
                'message': 'successful',
                'data': follower_serialized.data
            }

            return Response(response_json, status=200)

        if followings:
            following_objs = UserFollowing.objects.filter(user_id=user_id)

            following_serialized = UserFollowerSerializer(following_objs, many=True)

            response_json = {
                'status': True,
                'message': 'successful',
                'data': following_serialized.data
            }

            return Response(response_json, status=200)

        response_json = {
            'status': False,
            'message': 'unsuccessful',
            'data': {}
        }

        return Response(response_json, status=200)


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
                'password': make_password(new_password)
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
            user_follower_obj = UserFollower.objects.filter(user_id=user_id).first()
            if not user_follower_obj:
                return existence_error('follower')

            user_follower_obj.follower_user_id.add(request.user.id)

            # add user id to requested user followings
            user_following_obj = UserFollowing.objects.filter(user_id=request.user.id).first()
            if not user_following_obj:
                return existence_error('following')

            user_following_obj.following_user_id.add(user_id)

            response_json = {
                'status': True,
                'message': "successful",
                'data': {}
            }

            return Response(response_json, status=200)

        if not follow:
            # remove requested user from user id's followers
            user_follower_obj = UserFollower.objects.filter(user_id=user_id).first()
            if not user_follower_obj:
                return existence_error('follower')

            user_follower_obj.follower_user_id.remove(request.user.id)

            # remove user id from requested user followings
            user_following_obj = UserFollowing.objects.filter(user_id=request.user.id).first()
            if not user_following_obj:
                return existence_error('following')

            user_following_obj.following_user_id.remove(user_id)

            response_json = {
                'status': True,
                'message': "successful",
                'data': {}
            }

            return Response(response_json, status=200)


class ForgetPassword(APIView):

    def post(self, request):

        email = request.data.get('email').lower()
        code = generate_otp()

        user_obj = UserProfile.objects.filter(email=email)
        if not user_obj:
            return existence_error('user')

        request_json = {
            'email_phone': email,
            'code': code
        }

        otp_serialized = OtpSerializer(data=request_json)
        if not otp_serialized.is_valid():
            return validate_error(otp_serialized)
        otp_serialized.save()

        email_body = 'Here is your link to reset your password: http://94.100.28.185:3520/user/reset-password?code={0}'.format(code)

        send_email("Password reset", email_body, email)

        response_json = {
            'status': True,
            'message': "successful",
            'data': {}
        }

        return Response(response_json, status=200)


class ResetPassword(APIView):

    def post(self, request):

        code = request.GET.get('code')

        otp_obj = Otp.objects.filter(code=code).first()
        if otp_obj is None:
            return existence_error('verification_code')

        user_obj = UserProfile.objects.filter(email=otp_obj.email_phone).first()
        if user_obj is None:
            return existence_error('user')

        request_json = {
            'password': make_password(request.data.get('new_password'))
        }

        user_serialized = UserProfileSerializer(user_obj, data=request_json, partial=True)
        if not user_serialized.is_valid():
            return validate_error(user_serialized)
        user_serialized.save()

        otp_obj.delete()

        return Response({'succeeded': True}, status=200)

















