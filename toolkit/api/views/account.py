# -*- coding: UTF-8 -*-
from django.contrib.auth.models import User

from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.response import Response

from rulez import registry as rulez_registry

from ..serializers import AccountSerializer, PasswordSerializer


class AccountEndpoint(generics.RetrieveUpdateAPIView):
    """
    """
    queryset = User.objects.all()
    serializer_class = AccountSerializer

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    def get_object(self):
        return self.get_queryset().first()

    def get(self, request, **kwargs):
        user = self.get_object()
        serializer = self.serializer_class(user)
        return Response(serializer.data)

    def update(self, request, **kwargs):
        user = self.get_object()

        if 'password' in request.DATA:
            return self.set_password(password=request.DATA.pop('password'))

        serializer = self.serializer_class(user, data=request.DATA, partial=True)

        if serializer.is_valid():
            serializer.save()

        return Response(serializer.data)

    def set_password(self, password):
        """
        Update the users Account Password
        """
        user = self.get_object()
        serializer = PasswordSerializer(user, data={'password': password})

        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'password changed'})

        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def can_read(self, user):
        return user == self.get_object() or user.is_staff is True or user.is_superuser is True

    def can_edit(self, user):
        return user == self.get_object() or user.is_staff is True or user.is_superuser is True

    def can_delete(self, user):
        return user == self.get_object() or user.is_staff is True or user.is_superuser is True


rulez_registry.register("can_read", AccountEndpoint)
rulez_registry.register("can_edit", AccountEndpoint)
rulez_registry.register("can_delete", AccountEndpoint)
