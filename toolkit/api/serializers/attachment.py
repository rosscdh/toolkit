# -*- coding: UTF-8 -*-
from rest_framework import serializers

from toolkit.core.attachment.models import Revision


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Revision
        #exclude = ()
