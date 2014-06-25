# -*- coding: UTF-8 -*-
# from django.core.cache import cache
from django.core.exceptions import ValidationError

from rest_framework.reverse import reverse

from rest_framework import serializers
from urlparse import urlparse

from toolkit.core.attachment.models import Revision
from toolkit.core.attachment.tasks import _download_file
from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL

from toolkit.api.serializers.user import _get_user_review, _get_user_sign

from .user import SimpleUserSerializer
from .review import ReviewSerializer
from .sign import SignatureSerializer

import os
import logging
logger = logging.getLogger('django.request')

# should be as short as possible, to allow for the upload_to path as well as extension as well as other addons
MAX_LENGTH_FILENAME = 50
# list of extensions to accept
EXT_WHITELIST = ('.pdf', '.docx', '.doc', '.ppt', '.pptx', '.xls', '.xlsx')
# need to get a list of mimetypes for teh above


def _valid_filename_length(filename):
    """
    1. ensure length is max 85 (to account for 100 char limit in django filename fields)
    """

    original_filename = filename
    base_filename, ext = os.path.splitext(original_filename)
    ext = ext.lower()

    if ext not in EXT_WHITELIST:
        raise ValidationError("Invalid filetype, is: %s should be in: %s" % (ext, EXT_WHITELIST))

    if len(base_filename) > MAX_LENGTH_FILENAME:  # allow for 20 aspects to the name in addition ie. v1-etc
        base_filename = base_filename[0:MAX_LENGTH_FILENAME]

    return '%s%s' % (base_filename, ext)


class FileHasNoNameException(Exception):
    """
    Custom exception for handling files with no name specifically
    """
    pass


class LimitedExtensionMixin(object):
    """
    Same as forms.FileField, but you can specify a file extension whitelist.

    >>> from django.core.files.uploadedfile import SimpleUploadedFile
    >>>
    >>> t = ExtFileField(ext_whitelist=(".pdf", ".txt"))
    >>>
    >>> t.clean(SimpleUploadedFile('filename.pdf', 'Some File Content'))
    >>> t.clean(SimpleUploadedFile('filename.txt', 'Some File Content'))
    >>>
    >>> t.clean(SimpleUploadedFile('filename.exe', 'Some File Content'))
    Traceback (most recent call last):
    ...
    ValidationError: [u'Not allowed filetype!']
    """
    ext_whitelist = EXT_WHITELIST

    def __init__(self, *args, **kwargs):
        ext_whitelist = kwargs.pop("ext_whitelist", self.ext_whitelist)

        self.ext_whitelist = [i.lower() for i in ext_whitelist]

        super(LimitedExtensionMixin, self).__init__(*args, **kwargs)

    def validate_filename(self, value):
        if value is not None:

            value = getattr(value, 'name', value)  # handle in InMemoryUploadedFiles being passed in

            filename, ext = os.path.splitext(value)

            if ext in [None, '']:
                #
                # ok so we have no extension; thats weird it must be a filepickerio upload
                # try to extract it from the request.DATA
                #
                request = self.context.get('request', {})
                original_filename = request.DATA.get('name')
                filename, ext = os.path.splitext(original_filename)

            ext = ext.lower()

            if ext not in self.ext_whitelist:
                raise ValidationError("Invalid filetype, is: %s should be in: %s" % (ext, self.ext_whitelist))

    def from_native(self, value):
        value = super(LimitedExtensionMixin, self).from_native(value)
        self.validate_filename(value=value)
        return value


class HyperlinkedAutoDownloadFileField(LimitedExtensionMixin, serializers.URLField):
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
                    raise FileHasNoNameException('File has no name')

                #
                # Start download if the file does not exist
                #

                # important as we then access the "name" attribute in teh serializer
                # that allows us to name the file (as filepicker sends the name and url seperately)
                request = self.context.get('request', {})
                url = request.DATA.get('executed_file')

                original_filename = _valid_filename_length(request.DATA.get('name'))

                if original_filename is None:
                    #
                    # the name was not set; therefore extract it from executed_file which shoudl be a url at this point
                    #
                    try:
                        url_path = urlparse(request.DATA.get('executed_file'))
                    except:
                        # sometimes, yknow its not a url
                        url_path = request.DATA.get('executed_file')
                    original_filename = os.path.basename(url_path.path)

                #
                # NB! we pass this into download which then brings the filedown and names it in the precribed
                # upload_to manner
                #
                file_name, file_object = _download_file(url=url, filename=original_filename, obj=obj, obj_fieldname=field_name)
                field = getattr(obj, field_name)

                # NB! we reuse the original_filename!
                # this is to prevent filenames that repeat the original name twice
                field.save(original_filename, file_object)
                # update the object
                obj.save(update_fields=[field_name])

                return super(HyperlinkedAutoDownloadFileField, self).field_to_native(obj, field_name)

            except Exception as e:
                logger.debug('File serialized without a value: %s' % e)
        #
        # NB this must return None!
        # else it will raise attribute has no file associated with it
        # errors
        #
        return None


class FileFieldAsUrlField(LimitedExtensionMixin, serializers.FileField):
    """
    Acts like a normal FileField but to_native will download the file
    """
    def from_native(self, value):
        self.validate_filename(value=value.name)
        return super(FileFieldAsUrlField, self).from_native(value=value)

    def to_native(self, value):
        if hasattr(value, 'url') is True:
            #
            # Validate its of the right type
            #
            self.validate_filename(value=value.name)
            #
            # Just download the object, the rest gets handled naturally
            #
            if urlparse(value.url).scheme:  # check where delaing with an actual url here
                _download_file(url=value.url, filename=value.name, obj=value.instance)

        return getattr(value, 'url', super(FileFieldAsUrlField, self).to_native(value=value))


class RevisionSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField('get_custom_api_url')

    regular_url = serializers.Field(source='get_regular_url')

    executed_file = HyperlinkedAutoDownloadFileField(required=False)

    status = serializers.IntegerField(required=False)

    item = serializers.HyperlinkedRelatedField(many=False, view_name='item-detail')

    reviewers = serializers.SerializerMethodField('get_reviewers')
    signers = SimpleUserSerializer(source='signers.all', many=True, required=False)
    signing = serializers.SerializerMethodField('get_signing')

    user_review = serializers.SerializerMethodField('get_user_review')
    user_download_url = serializers.SerializerMethodField('get_user_download_url')

    revisions = serializers.SerializerMethodField('get_revisions')

    uploaded_by = serializers.SerializerMethodField('get_uploaded_by')

    date_created = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Revision
        fields = ('slug',
                  'url', 'regular_url',
                  'name', 'description',
                  'executed_file',
                  'is_executed',
                  'status',
                  'item',
                  'uploaded_by',
                  'reviewers', 'signers',
                  'signing',
                  'revisions',
                  'user_review', 'user_download_url',
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
            if request:
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

    def validate_executed_file(self, attrs, source):
        """
        Ensure is valid length filename 100 is the max length
        """
        executed_file = attrs.get(source)
        if executed_file is not None and type(executed_file) not in [str, unicode]:
            executed_file.name = _valid_filename_length(executed_file.name)
            attrs[source] = executed_file

        return attrs

    def get_custom_api_url(self, obj):
        return ABSOLUTE_BASE_URL(reverse('matter_item_specific_revision',
                                         kwargs={'matter_slug': obj.item.matter.slug,
                                                 'item_slug': obj.item.slug,
                                                 'version': obj.slug.replace('v', '')}))

    def get_uploaded_by(self, obj):
        return SimpleUserSerializer(obj.uploaded_by, context={'request': self.context.get('request')}).data

    def get_reviewers(self, obj):
        reviewers = []
        if getattr(obj, 'pk', None) is not None:  # it has not been deleted when pk is None
            for reviewdoc in obj.reviewdocument_set.filter(reviewers__in=obj.reviewers.all()):
                reviewers.append(ReviewSerializer(reviewdoc, context={'request': self.context.get('request')}).data)

        return reviewers

    def get_user_review(self, obj):
        """
        Try to provide an initial reivew url from the base review_document obj
        for the currently logged in user
        """
        context = getattr(self, 'context', None)
        request = context.get('request')

        review_document = _get_user_review(self=self, obj=obj, context=context)

        if review_document is not None:

            return_object = {
                'url': review_document.get_absolute_url(user=request.user),
                'slug': review_document.slug,
            }

            # #
            # # test for sign_in_progress and change the url if present
            # #
            # if self._sign_in_progress(obj=obj) is not False:
            #     return_object.update({'url': reverse('sign:sign_in_progress')})

            return return_object

    def get_user_download_url(self, obj):
        """
        Try to provide the download url for the users revision
        for the currently logged in user
        """
        context = getattr(self, 'context', None)
        request = context.get('request')

        review_document = _get_user_review(self=self, obj=obj, context=context)

        if review_document is not None:
            return review_document.get_download_url(user=request.user)

        return None

    # def _sign_in_progress(self, obj):
    #     """
    #     retrieve the cached sign_in_progress-%s key
    #     @NB ties in with sign.views:handle_sign_in_progress
    #     """
    #     return cache.get(obj.SIGN_IN_PROGRESS_KEY, False)

    def get_signing(self, obj):
        data = None
        context = getattr(self, 'context', None)

        sign_document = _get_user_sign(self=self, obj=obj, context=context)

        if sign_document is not None and sign_document.signing_request is not None:
            data = SignatureSerializer(sign_document, context=context).data

        # if data:
        #     data.update({'in_progress': self._sign_in_progress(obj=obj)})

        return data


    def get_revisions(self, obj):
        return [ABSOLUTE_BASE_URL(reverse('matter_item_specific_revision', kwargs={
                    'matter_slug': obj.item.matter.slug,
                    'item_slug': obj.item.slug,
                    'version': c + 1
                })) for c, revision in enumerate(obj.revisions) if revision.pk != obj.pk]


class SimpleRevisionSerializer(RevisionSerializer):
    class Meta(RevisionSerializer.Meta):
        fields = ('slug',
                  'url', 'regular_url',
                  'name',
                  'status',
                  'date_created',)

