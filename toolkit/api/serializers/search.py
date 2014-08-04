# -*- coding: UTF-8 -*-
from django.template.defaultfilters import truncatewords
from rest_framework import serializers


class MatterSearchSerializer(serializers.Serializer):
    """
    A unified serializer to combine matter.items(name,description); matter.item.tasks(name,description)
    and matter.item.attachments(name)
    into a single unified search stream
    """
    file_type = serializers.SerializerMethodField('get_file_type')
    name = serializers.SerializerMethodField('get_name')
    description = serializers.SerializerMethodField('get_description')
    url = serializers.SerializerMethodField('get_url')

    def get_file_type(self, obj):
        return obj.__class__.__name__

    def get_name(self, obj):
        if obj.__class__.__name__ in ['Item', 'Revision', 'Task', 'Attachment']:
            return obj.name
        return None

    def get_description(self, obj):
        if obj.__class__.__name__ in ['Item', 'Revision', 'Task']:
            return truncatewords(obj.description, 7)
        return None

    def get_url(self, obj):
        if obj.__class__.__name__ in ['Item', 'Revision', 'Task', 'Attachment']:
            return obj.get_absolute_url()
        return None
