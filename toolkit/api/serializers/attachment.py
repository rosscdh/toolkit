# -*- coding: UTF-8 -*-
from rest_framework import serializers

from toolkit.core.attachment.models import Attachment

from .user import SimpleUserSerializer

from .revision import HyperlinkedAutoDownloadFileField, FileFieldAsUrlField  # TODO: move to a place for reusable stuff?

import logging
logger = logging.getLogger('django.request')


class AttachmentSerializer(serializers.HyperlinkedModelSerializer):
    # url = serializers.SerializerMethodField('get_custom_api_url')
    # regular_url = serializers.Field(source='get_regular_url')

    file = HyperlinkedAutoDownloadFileField(file_field_name='file', required=False)

    item = serializers.HyperlinkedRelatedField(many=False, view_name='item-detail')

    uploaded_by = serializers.SerializerMethodField('get_uploaded_by')

    date_created = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Attachment
        fields = (#'url', 'regular_url',
                  'name',
                  'file',
                  'item',
                  'uploaded_by',
                  'date_created',)



    # def __init__(self, *args, **kwargs):
    #     #
    #     # @TODO turn these into nice clean methods
    #     #
    #     self.base_fields['file'] = HyperlinkedAutoDownloadFileField(required=False)
    #     self.base_fields['uploaded_by'] = SimpleUserSerializer()
    #     #
    #     # If we are passing in a multipart form
    #     #
    #     if 'context' in kwargs and 'request' in kwargs['context']:
    #         request = kwargs['context'].get('request')
    #         if request:
    #             #
    #             # set the executed_file field to be a seriallizer.FileField and behave like one of those
    #             #
    #             if request.method in ['PATCH', 'POST']:
    #                 # ensure the uploaded_by is just a simple hyplinkrelatedfield on update,create
    #                 self.base_fields['uploaded_by'] = serializers.HyperlinkedRelatedField(many=False,
    #                                                                                       view_name='user-detail',
    #                                                                                       lookup_field='username')
    #
    #                 if 'multipart/form-data;' in kwargs['context']['request'].content_type:
    #                     if kwargs['context']['request'].FILES:
    #                         self.base_fields['file'] = FileFieldAsUrlField(allow_empty_file=True, required=False)
    #
    #     super(AttachmentSerializer, self).__init__(*args, **kwargs)



    # def validate_executed_file(self, attrs, source):
    #     """
    #     Ensure is valid length filename 100 is the max length
    #     """
    #     executed_file = attrs.get(source)
    #     if executed_file is not None and type(executed_file) not in [str, unicode]:
    #         executed_file.name = _valid_filename_length(executed_file.name)
    #         attrs[source] = executed_file
    #
    #     return attrs
    #
    # def get_custom_api_url(self, obj):
    #     return ABSOLUTE_BASE_URL(reverse('matter_item_specific_revision',
    #                                      kwargs={'matter_slug': obj.item.matter.slug,
    #                                              'item_slug': obj.item.slug,
    #                                              'version': obj.slug.replace('v', '')}))

    def get_uploaded_by(self, obj):
        return SimpleUserSerializer(obj.uploaded_by, context={'request': self.context.get('request')}).data