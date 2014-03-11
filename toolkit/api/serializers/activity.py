# -*- coding: utf-8 -*-
from actstream.models import Action
from rest_framework import serializers

__author__ = 'Marius Burfey <marius.burfey@ambient-innovation.com> - 11.03.14'


class ActivitySerializer(serializers.HyperlinkedModelSerializer):
    """
    """
    class Meta:
        model = Action