# -*- coding: UTF-8 -*-
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework import generics
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import status as http_status

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

    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', 'email',)

    def get_object(self):
        queryset = self.get_queryset()
        username = self.kwargs.get('username', None)
        if username is not None:
            return get_object_or_404(User, username=username)
        return queryset.none()

    def list(self, request, **kwargs):
        if request.GET.get('search', None) is not None:
            return super(UserEndpoint, self).list(request=request, **kwargs)
        return Response(None, status=http_status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_serializer_context(self):
        return {'request': self.request}

    def can_read(self, user):
        return user.is_authenticated()

    def can_edit(self, user):
        self.object = self.get_object()
        if self.object:
            return user.id == self.object.id
        return False

    def can_delete(self, user):
        return user.is_staff or user.is_superuser


rulez_registry.register("can_read", UserEndpoint)
rulez_registry.register("can_edit", UserEndpoint)
rulez_registry.register("can_delete", UserEndpoint)