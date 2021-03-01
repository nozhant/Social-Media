from rest_framework.serializers import ModelSerializer, SerializerMethodField

from user.models import UserProfile, Otp, UserFollowing, UserFollower


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

    class Meta:
        model = UserProfile
        exclude = ('password', 'groups', 'user_permissions', 'is_staff', 'phone_number', 'email',
                   'last_login',
                   'is_superuser', 'join_date', 'is_active', 'two_step')


class UserProfileForPostSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'name', 'last_name', 'profile_photo', 'business', 'country', 'city']


class EditUserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('username', 'name', 'last_name', 'bio', 'website', 'email', 'phone_number', 'profile_photo', 'business', 'country', 'city')


class UserFollowingSerializer(ModelSerializer):

    class Meta:
        model = UserFollowing
        fields = '__all__'


class UserFollowerSerializer(ModelSerializer):

    class Meta:
        model = UserFollower
        fields = '__all__'


class UserFollowingShowSerializer(ModelSerializer):
    following_user_id = UserProfileShowSerializer(many=True)

    class Meta:
        model = UserFollowing
        fields = '__all__'


class UserFollowerShowSerializer(ModelSerializer):
    follower_user_id = UserProfileShowSerializer(many=True)

    class Meta:
        model = UserFollower
        fields = '__all__'


class OtpSerializer(ModelSerializer):
    class Meta:
        model = Otp
        fields = '__all__'
