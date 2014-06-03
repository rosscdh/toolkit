# -*- coding: utf-8 -*-
from django.shortcuts import render

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.renderers import UnicodeJSONRenderer

from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet

from .serializers import SearchResultSerializer


class SearchResultsView(generics.ListAPIView):
    serializer_class = SearchResultSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """
        SearchQuerySet().filter(text=AutoQuery('crawford -date_created'))
        """
        query = self.request.GET.get('q')
        return SearchQuerySet().filter(text=AutoQuery(query))

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        object_list = self.get_serializer(self.get_queryset(), many=True).data
        return Response(object_list)