# -*- coding: UTF-8 -*-
from rest_framework import serializers

from django.contrib.auth.models import User


class AccountSerializer(serializers.ModelSerializer):
    user_class = serializers.CharField(source='profile.user_class', read_only=True)

    class Meta:
        model = User
        fields = ('last_login', 'username', 'first_name', 'last_name', 'email', 'date_joined', 'user_class',)


class PasswordSerializer(serializers.Serializer):
    pass