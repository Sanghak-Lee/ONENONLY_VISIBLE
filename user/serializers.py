from rest_framework import serializers
from .models import Users
from artist import models

class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    class Meta:
        model = Users
        fields = (
            "id",
            "date_joined",
            "username",
            "email",
            "password",
        )
        read_only_fields = ("id", "date_joined")

    
    def validate_email(self, value):
        return value.upper()

    def create(self, validated_data):
        password = validated_data.get("password")
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user



