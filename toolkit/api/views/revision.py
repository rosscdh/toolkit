# -*- coding: UTF-8 -*-
from rest_framework.views import APIView
from rest_framework.response import Response

from ..serializers import RevisionSerializer


class Endpoint(APIView):
    """
    """

    def post(self, request, format=None):
        """
        """
        resp = {}
        return Response(resp)