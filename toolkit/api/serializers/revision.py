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
        try:
            return request.build_absolute_uri(value.url) 
        except ValueError:
            return None


class RevisionSerializer(serializers.HyperlinkedModelSerializer):
    revision_id = serializers.CharField(source='slug', read_only=True)

    executed_file = HyperlinkedFileField(allow_empty_file=False)
    item = serializers.HyperlinkedRelatedField(many=False, view_name='item-detail')

    reviewers = serializers.HyperlinkedRelatedField(many=True, view_name='user-detail', lookup_field='username')
    signatories = serializers.HyperlinkedRelatedField(many=True, view_name='user-detail', lookup_field='username')

    revisions = serializers.SerializerMethodField('get_revisions')

    uploaded_by = serializers.HyperlinkedRelatedField(many=False, view_name='user-detail', lookup_field='username')

    class Meta:
        model = Revision
        fields = ('url',
                  'revision_id', 'executed_file', 
                  'item', 'uploaded_by', 
                  'reviewers', 'signatories',
                  'revisions',
                  'date_created', 'date_modified',)

    def get_revisions(self, obj):
        return [reverse('matter_item_specific_revision', kwargs={
                'matter_slug': obj.item.matter.slug,
                'item_slug': obj.item.slug,
                'version': c + 1
        }) for c, revision in enumerate(obj.revisions) if revision.pk != obj.pk]
        #}) for c, revision in enumerate(obj.revisions)]
