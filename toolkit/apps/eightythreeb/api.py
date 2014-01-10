# -*- coding: UTF-8 -*-
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import DestroyAPIView
from rest_framework.mixins import UpdateModelMixin

from toolkit.apps.workspace.mixins import IssueSignalsMixin

from .models import EightyThreeB, Attachment
from .serializers import EightyThreeBSerializer, AttachmentSerializer

import logging
logger = logging.getLogger('django.request')


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
                status = self.request.DATA.get('status', None)

                if status is None:
                    logger.error('No status passed in for 83(b) "%s" by "%s"' % (self.object, request.user))

                else:
                    markers = self.object.markers
                    # retrieve the marker by value so we can get its name
                    marker = markers.marker_by_val(val=status)

                    if marker is None:
                        logger.error('Could not get a marker for 83(b) "%s" based on the status "%s" by "%s"' % (self.object, status, request.user))

                    else:
                        # issue the signal
                        self.issue_signals(request=request, instance=self.object, name=marker.name)

        return super(EightyThreeBViewSet, self).finalize_response(request, response, *args, **kwargs)


class AttachmentDeleteView(DestroyAPIView, UpdateModelMixin):
    """
    api view to allow user to "delete" an attachment associated with an 83b
    """
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer