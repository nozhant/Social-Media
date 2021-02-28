from rest_framework.serializers import ModelSerializer

from user.models import UserProfile, Otp


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserProfileShowSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        exclude = (
            'password', 'groups', 'user_permissions', 'is_staff', 'phone_number', 'email', 'last_login', 'is_superuser',
            'join_date', 'is_active'
        )


class UserProfileGetSerializer(ModelSerializer):
    following = UserProfileShowSerializer(many=True)
    follower = UserProfileShowSerializer(many=True)

    class Meta:
        model = UserProfile
        exclude = ('password', 'groups', 'user_permissions', 'is_staff', 'phone_number', 'email',
                   'last_login',
                   'is_superuser', 'join_date', 'is_active', 'two_step')


class UserProfileForPostSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'name', 'last_name', 'profile_photo', 'business', 'country', 'cit']


class EditUserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('username', 'name', 'last_name', 'bio', 'website', 'email', 'phone_number', 'profile_photo', 'business', 'country', 'city')


class OtpSerializer(ModelSerializer):
    class Meta:
        model = Otp
        fields = '__all__'
