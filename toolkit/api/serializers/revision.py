# -*- coding: UTF-8 -*-
from django.core.files import File
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator
from django.core.files.temp import NamedTemporaryFile


from rest_framework import serializers

from toolkit.core.attachment.tasks import _download_file
from toolkit.core.attachment.models import Revision

import logging
logger = logging.getLogger('django.request')


class HyperlinkedFileField(serializers.FileField):
    """
    Custom FieldField to allow us to show the FileField url and not its std
    representation
    """
    def to_native(self, value):
        request = self.context.get('request', None)
        if request is not None and value is not None:
            try:
                return request.build_absolute_uri(value.url)
            except ValueError:
                logger.info('No url associated with this file: %s' % value)
                pass

        return None


class HyperlinkedAutoDownloadFileField(serializers.URLField):
    """
    Autodownload a file specified by a url
    """
    def field_to_native(self, obj, field_name):
        if obj is not None:
            field = getattr(obj, field_name)

            try:
                if field.name in [None, '']:
                    raise Exception('File has no name')

                # Validate the url
                URLValidator(field.name)

                #
                # Start download if the file does not exist
                #
                _download_file(url=field.name, obj=obj, obj_fieldname=field_name)

                # set to blank so we dont get Suspicious operation on urls
                field.file = File(NamedTemporaryFile())
                setattr(obj, field_name, field)
                return super(HyperlinkedAutoDownloadFileField, self).field_to_native(obj, field_name)
            except Exception as e:
                #
                # is probably a normal file at this point but jsut continue to be safe
                #
                logger.info('HyperlinkedAutoDownloadFileField field.name is not a url: %s' % field)


class RevisionSerializer(serializers.HyperlinkedModelSerializer):
    executed_file = HyperlinkedFileField(allow_empty_file=True, required=False)
    item = serializers.HyperlinkedRelatedField(many=False, view_name='item-detail')

    reviewers = serializers.HyperlinkedRelatedField(many=True, view_name='user-detail', lookup_field='username')
    signatories = serializers.HyperlinkedRelatedField(many=True, view_name='user-detail', lookup_field='username')

    user_review_url = serializers.SerializerMethodField('get_user_review_url')
    revisions = serializers.SerializerMethodField('get_revisions')

    uploaded_by = serializers.HyperlinkedRelatedField(many=False, view_name='user-detail', lookup_field='username')

    # date_created = serializers.DateTimeField(read_only=True)
    # date_modified = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Revision
        fields = ('url', 'slug',
                  'executed_file', 
                  'item', 'uploaded_by', 
                  'reviewers', 'signatories',
                  'revisions', 'user_review_url',)
                  #'date_created', 'date_modified',)

    def __init__(self, *args, **kwargs):
        self.base_fields['executed_file'] = HyperlinkedFileField(allow_empty_file=True, required=False)
        #
        # If we are passing in a multipart form
        #
        if 'request' in kwargs['context']:

            request = kwargs['context'].get('request')

            if request.method in ['PATCH', 'POST']:

                self.base_fields['executed_file'] = HyperlinkedAutoDownloadFileField(required=False)
                #
                # set the executed_file field to be a seriallizer.FileField and behave like one of those
                #
                if 'multipart/form-data;' in kwargs['context']['request'].content_type:
                    if kwargs['context']['request'].FILES:
                        self.base_fields['executed_file'] = serializers.FileField(allow_empty_file=True, required=False)

        super(RevisionSerializer, self).__init__(*args, **kwargs)

    def get_user_review_url(self, obj):
        """
        Try to provide an initial reivew url from the base review_document obj
        """
        context = getattr(self, 'context', None)
        request = context.get('request')

        if request is not None:
            initial_reviewdocument = obj.reviewdocument_set.all().first()
            return initial_reviewdocument.get_absolute_url(user=request.user)

        return None

    def get_revisions(self, obj):
        return [reverse('matter_item_specific_revision', kwargs={
                'matter_slug': obj.item.matter.slug,
                'item_slug': obj.item.slug,
                'version': c + 1
        }) for c, revision in enumerate(obj.revisions) if revision.pk != obj.pk]
        #}) for c, revision in enumerate(obj.revisions)]
