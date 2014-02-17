# -*- coding: UTF-8 -*-
from rest_framework import viewsets
from rest_framework.response import Response

from django.contrib.auth.models import User
from ..serializers import UserSerializer


class UserEndpoint(viewsets.ModelViewSet):
    """
    """
    model = User
    lookup_field = 'username'
    serializer_class = UserSerializer