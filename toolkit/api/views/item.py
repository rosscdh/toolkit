# -*- coding: UTF-8 -*-
from rest_framework.views import APIView
from rest_framework.response import Response

from ..serializers import ItemSerializer


class ItemEndpoint(APIView):
    """
    """
    def get(self, request, format=None):
        """
        """
        resp = {}
        return Response(resp)

    def patch(self, request, format=None):
        """
        """
        resp = {}
        return Response(resp)

    def post(self, request, format=None):
        """
        """
        resp = {}
        return Response(resp)

    def delete(self, request, format=None):
        """
        """
        resp = {}
        return Response(resp)