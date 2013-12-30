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
            # get the tools markers
            markers = self.object.markers
            # retrieve the marker by value so we can get its name
            marker = markers.marker_by_val(val=self.request.DATA.get('status'))
            # issue the signal
            self.issue_signals(request=request, instance=self.object, name=marker.name)

        return super(EightyThreeBViewSet, self).finalize_response(request, response, *args, **kwargs)