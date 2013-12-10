# -*- coding: UTF-8 -*-
from rest_framework.viewsets import ModelViewSet

from toolkit.apps.workspace.mixins import IssueSignalsMixin

from .models import EightyThreeB
from .serializers import EightyThreeBSerializer


class EightyThreeBViewSet(IssueSignalsMixin, ModelViewSet):
    """
    """
    queryset = EightyThreeB.objects.all()
    serializer_class = EightyThreeBSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        """
        emit the issue_signals
        """
        if response.status_code in [200, 201]:
            self.issue_signals(request=request, instance=self.object)

        return super(EightyThreeBViewSet, self).finalize_response(request, response, *args, **kwargs)