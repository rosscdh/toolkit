# -*- coding: UTF-8 -*-
from rest_framework import serializers

from django.contrib.auth.models import User


class AccountSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    user_class = serializers.CharField(source='profile.user_class', read_only=True)

    class Meta:
        model = User
        fields = ('last_login', 'username', 'first_name', 'last_name', 'email', 'date_joined', 'user_class',)


class PasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('password',)

    def save_object(self, obj, **kwargs):
        obj.set_password(self.data.get('password'))
        obj.save(update_fields=['password'])