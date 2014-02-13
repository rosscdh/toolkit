# -*- coding: UTF-8 -*-
"""
Matters are workspaces; and are composted of items, which may be a todo item
or a document item
"""
from rest_framework import serializers

from toolkit.apps.workspace.models import Workspace


class MatterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        #exclude = ()
