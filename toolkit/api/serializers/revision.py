# -*- coding: UTF-8 -*-
from django.core.files import File
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator
from django.core.files.temp import NamedTemporaryFile

from rest_framework import serializers

from toolkit.core.attachment.tasks import _download_file
from toolkit.core.attachment.models import Revision

from .user import SimpleUserSerializer

import logging
logger = logging.getLogger('django.request')


class HyperlinkedAutoDownloadFileField(serializers.URLField):
    """
    Autodownload a file specified by a url
    but also return just the url and not the FileObject on to_native unless it
    does not exist
    """
    def to_native(self, value):
        return getattr(value, 'url', value)

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
        #
        # NB this must return None!
        # else it will raise attribute has no file associated with it
        # errors
        #
        return None

class FileFieldAsUrlField(serializers.FileField):
    """
    Acts like a normal FileField but to_native will return the url if it exists
    otherwise if url not present just behave normally
    """
    def to_native(self, value):
        return getattr(value, 'url', super(FileFieldAsUrlField, self).to_native(value=value))


class RevisionSerializer(serializers.HyperlinkedModelSerializer):
    executed_file = HyperlinkedAutoDownloadFileField(required=False)

    status = serializers.ChoiceField(required=False)

    item = serializers.HyperlinkedRelatedField(many=False, view_name='item-detail')

    reviewers = serializers.HyperlinkedRelatedField(many=True, view_name='user-detail', lookup_field='username')
    signatories = serializers.HyperlinkedRelatedField(many=True, view_name='user-detail', lookup_field='username')

    user_review_url = serializers.SerializerMethodField('get_user_review_url')
    revisions = serializers.SerializerMethodField('get_revisions')

    uploaded_by = SimpleUserSerializer()

    date_created = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Revision
        fields = ('url', 'slug',
                  'name', 'description',
                  'executed_file', 
                  'status', 
                  'item', 'uploaded_by', 
                  'reviewers', 'signatories',
                  'revisions', 'user_review_url',
                  'date_created',)

    def __init__(self, *args, **kwargs):
        #
        # @TODO turn these into nice clean methods
        #
        self.base_fields['executed_file'] = HyperlinkedAutoDownloadFileField(required=False)
        self.base_fields['uploaded_by'] = SimpleUserSerializer()
        #
        # If we are passing in a multipart form
        #
        if 'context' in kwargs and 'request' in kwargs['context']:

            request = kwargs['context'].get('request')

            #
            # set the executed_file field to be a seriallizer.FileField and behave like one of those
            #
            if request.method in ['PATCH', 'POST']:

                # ensure the uploaded_by is just a simple hyplinkrelatedfield on update,create
                self.base_fields['uploaded_by'] = serializers.HyperlinkedRelatedField(many=False, view_name='user-detail', lookup_field='username')

                if 'multipart/form-data;' in kwargs['context']['request'].content_type:
                    if kwargs['context']['request'].FILES:
                        self.base_fields['executed_file'] = FileFieldAsUrlField(allow_empty_file=True, required=False)

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
