# -*- coding: UTF-8 -*-
from rest_framework import serializers

from toolkit.core.attachment.models import Revision


class RevisionSerializer(serializers.ModelSerializer):
    revision_id = serializers.CharField(source='revision_id', read_only=True)
    uploaded_by = serializers.HyperlinkedRelatedField(many=False, view_name='user-detail', lookup_field='username', read_only=True)
    item = serializers.HyperlinkedRelatedField(many=False, view_name='item-detail')

    reviewers = serializers.HyperlinkedRelatedField(many=True, view_name='user-detail', lookup_field='username')
    signatories = serializers.HyperlinkedRelatedField(many=True, view_name='user-detail', lookup_field='username')


    class Meta:
        model = Revision
        exclude = ('id', 'data', 'revisions')
