# -*- coding: UTF-8 -*-
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response

from ..serializers import AccountSerializer, PasswordSerializer


class AccountEndpoint(APIView):
    """
    """
    queryset = User.objects.all()
    serializer_class = AccountSerializer

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    def get_object(self):
        return self.get_queryset().first()

    def get(self, request, format=None):
        user = self.get_object()
        serializer = self.serializer_class(user)
        return Response(serializer.data)

    def update(self, request, format=None):
        user = self.get_object()
        serializer = self.serializer_class(user, data=request.DATA, partial=True)
        return Response(serializer.data)

    @action()
    def set_password(self, request):
        """
        Update the users Account Password
        """
        user = self.get_object()
        serializer = PasswordSerializer(data=request.DATA)

        if serializer.is_valid():
            user.set_password(serializer.data['password'])
            user.save()
            return Response({'status': 'password changed'})

        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)