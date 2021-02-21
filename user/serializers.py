from rest_framework.serializers import ModelSerializer

from user.models import UserProfile, Otp


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class OtpSerializer(ModelSerializer):
    class Meta:
        model = Otp
        fields = '__all__'