# -*- coding: UTF-8 -*-
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import generics

from django.contrib.auth.models import User
from ..serializers import UserSerializer

from rulez import registry as rulez_registry


class UserEndpoint(viewsets.ModelViewSet,
                   generics.RetrieveAPIView,
                   generics.UpdateAPIView,):
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

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(User, username=self.kwargs['username'])
        return obj

    def get_serializer_context(self):
        return {'request': self.request}

    def can_read(self, user):
        return user.is_authenticated()

    def can_edit(self, user):
        self.object = self.get_object()
        return user.id == self.object.id

    def can_delete(self, user):
        return user.is_staff or user.is_superuser

rulez_registry.register("can_read", UserEndpoint)
rulez_registry.register("can_edit", UserEndpoint)
rulez_registry.register("can_delete", UserEndpoint)