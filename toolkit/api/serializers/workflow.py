# -*- coding: UTF-8 -*-
"""
Workflows are representaion of the various Tools Markers and generic Markers
we have
"""
from rest_framework import serializers

from toolkit.apps.attachment.models import Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        #exclude = ()
