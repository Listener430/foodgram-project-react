from rest_framework import serializers as sr
from djoser import serializers

from foodgram.models import Follow
from .models import User


class CustomUserSerializer(serializers.UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "last_name",
            "first_name",
            "password",
        )


class CustomUserListSerializer(serializers.UserCreateSerializer):

    is_subscribed = sr.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "last_name",
            "first_name",
            "password",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()
