# -*- coding: UTF-8 -*-
from django.core.urlresolvers import reverse

from rest_framework import serializers

from toolkit.core.attachment.models import Attachment

from .user import SimpleUserSerializer
from .revision import HyperlinkedAutoDownloadFileField, FileFieldAsUrlField  # TODO: move to a place for reusable stuff?
from .revision import EXT_WHITELIST

ATTACHMENT_EXT_WHITELIST = EXT_WHITELIST + ('.gif', '.jpg', '.jpeg', '.png',)

import logging
logger = logging.getLogger('django.request')


class AttachmentSerializer(serializers.HyperlinkedModelSerializer):
    attachment = HyperlinkedAutoDownloadFileField(file_field_name='attachment', whitelist=ATTACHMENT_EXT_WHITELIST, required=True)

    item = serializers.HyperlinkedRelatedField(many=False, view_name='item-detail')
    uploaded_by = SimpleUserSerializer(many=False)

    user_download_url = serializers.SerializerMethodField('get_user_download_url')

    date_created = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Attachment
        exclude = ('is_deleted', 'data',)

    def __init__(self, *args, **kwargs):
        #
        # @TODO turn these into nice clean methods
        #
        self.base_fields['attachment'] = HyperlinkedAutoDownloadFileField(file_field_name='attachment', whitelist=ATTACHMENT_EXT_WHITELIST, required=True)  # reset the field
        self.base_fields['uploaded_by'] = SimpleUserSerializer(many=False)  # reset the field
        #
        # If we are passing in a multipart form
        #
        if 'context' in kwargs and 'request' in kwargs['context']:
            request = kwargs['context'].get('request')

            if request:
                #
                # set the executed_file field to be a seriallizer.FileField and behave like one of those
                #
                if request.method in ['PATCH', 'POST']:
                    # ensure the uploaded_by is just a simple hyplinkrelatedfield on update,create
                    self.base_fields['uploaded_by'] = serializers.SlugRelatedField(many=False,
                                                                                   slug_field='username')

                    if 'multipart/form-data;' in kwargs['context']['request'].content_type:
                        if kwargs['context']['request'].FILES:
                            self.base_fields['attachment'] = FileFieldAsUrlField(whitelist=ATTACHMENT_EXT_WHITELIST,
                                                                                 file_field_name='attachment',
                                                                                 allow_empty_file=True,
                                                                                 required=False)

        super(AttachmentSerializer, self).__init__(*args, **kwargs)

    def get_uploaded_by(self, obj):
        return SimpleUserSerializer(obj.uploaded_by, context={'request': self.context.get('request')}).data

    def get_user_download_url(self, obj):
        return reverse('download_attachment', kwargs={'slug': obj.slug})
