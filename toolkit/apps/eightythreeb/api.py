# -*- coding: UTF-8 -*-
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import DestroyAPIView
from rest_framework.mixins import UpdateModelMixin

from toolkit.apps.workspace.mixins import IssueSignalsMixin

from .models import EightyThreeB, Attachment
from .serializers import EightyThreeBSerializer, AttachmentSerializer


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
            if hasattr(self, 'object'):
                # get the tools markers
                markers = self.object.markers
                # retrieve the marker by value so we can get its name
                marker = markers.marker_by_val(val=self.request.DATA.get('status'))
                # issue the signal
                self.issue_signals(request=request, instance=self.object, name=marker.name)

        return super(EightyThreeBViewSet, self).finalize_response(request, response, *args, **kwargs)


class AttachmentDeleteView(DestroyAPIView, UpdateModelMixin):
    """
    api view to allow user to "delete" an attachment associated with an 83b
    """
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer

    def destroy(self, request, *args, **kwargs):
        """
        Override the destroy method as we want to updated is_deleted
        not actaully delete the object
        """
        # manually set the is_deleted True
        request.DATA['is_deleted'] = True

        # partial_update because were PATCHING the object
        return self.partial_update(request, *args, **kwargs)