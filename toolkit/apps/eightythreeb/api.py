# -*- coding: UTF-8 -*-
from rest_framework.viewsets import ModelViewSet

from .models import EightyThreeB
from .serializers import EightyThreeBSerializer


class EightyThreeBViewSet(ModelViewSet):
    """
    """
    queryset = EightyThreeB.objects.all()
    serializer_class = EightyThreeBSerializer

    # def get_queryset(self):
    #     qs = super(EightyThreeBViewSet, self).get_queryset()
    #     return qs.filter(user=self.request.user)
