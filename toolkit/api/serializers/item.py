# -*- coding: UTF-8 -*-
"""
Items are either todo items or document items
"""
from rest_framework import serializers

from toolkit.apps.item.models import Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        #exclude = ()
