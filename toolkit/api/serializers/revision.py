# -*- coding: UTF-8 -*-
"""
Revisions are representaions of an attachment; each revision may or may not have
changes in them; Revisions are to behave in a linked list fashion with 
.previous() and .next() implementations
"""
from rest_framework import serializers

from toolkit.apps.attachment.models import Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        #exclude = ()
