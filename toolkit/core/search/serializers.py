# -*- coding: UTF-8 -*-
"""
Serializer for search results dropdown
"""
from django.core.urlresolvers import reverse

from rest_framework import serializers


class SearchResultSerializer(serializers.Serializer):
    name = serializers.SerializerMethodField('get_name')
    url = serializers.SerializerMethodField('get_url')
    description = serializers.SerializerMethodField('get_short_description')
    result_type = serializers.SerializerMethodField('get_result_type')

    def get_url(self, obj):
        return obj.get_additional_fields().get('url')

    def get_name(self, obj):
        return obj.get_additional_fields().get('name')

    def get_short_description(self, obj):
        return obj.get_additional_fields().get('description', None)

    def get_result_type(self, obj):
        return obj._get_verbose_name()