from rest_framework.serializers import ModelSerializer

from user.models import UserProfile, Otp


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserProfileShowSerializer(ModelSerializer):

    class Meta:
        model = UserProfile
        exclude = ('password', 'groups', 'user_permissions', 'is_staff', 'phone_number', 'email',)


class UserProfileGetSerializer(ModelSerializer):
    following = UserProfileShowSerializer(many=True)
    follower = UserProfileShowSerializer(many=True)

    class Meta:
        model = UserProfile
        exclude = ('password', 'groups', 'user_permissions', 'is_staff', 'phone_number', 'email',)


class OtpSerializer(ModelSerializer):
    class Meta:
        model = Otp
        fields = '__all__'
