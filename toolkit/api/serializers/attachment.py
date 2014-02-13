# -*- coding: UTF-8 -*-
from rest_framework import serializers

from toolkit.apps.attachment.models import Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        #exclude = ()
