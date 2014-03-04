# -*- coding: UTF-8 -*-
from rest_framework.views import APIView
from rest_framework.response import Response

from ..serializers import WorkflowSerializer


class MatterEndpoint(APIView):
    """
    """
    def get(self, request, format=None):
        """
        """
        resp = {}
        return Response(resp)
