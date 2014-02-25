# -*- coding: UTF-8 -*-
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from django.contrib.auth.models import User
from ..serializers import UserSerializer


class UserEndpoint(viewsets.ModelViewSet):
    """
    """
    model = User
    lookup_field = 'username'
    serializer_class = UserSerializer

    # def list(self, request, **kwargs):
    #     """
    #     @BUSINESSRULE only admin and superusers can see the list of users
    #     """
    #     user = request.user
    #     if user.is_staff is True or user.is_superuser is True:
    #         return super(UserEndpoint, self).list(request=request, **kwargs)

    #     raise PermissionDenied()