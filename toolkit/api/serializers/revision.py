# -*- coding: UTF-8 -*-
from django.core.urlresolvers import reverse

from rest_framework import serializers

from toolkit.core.attachment.models import Revision


class HyperlinkedFileField(serializers.FileField): 
    """
    Custom FieldField to allow us to show the FileField url and not its std
    representation
    """
    def to_native(self, value):
        request = self.context.get('request', None) 
        if request is not None:
            try:
                return request.build_absolute_uri(value.url) 
            except ValueError:
                pass

        return None


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
