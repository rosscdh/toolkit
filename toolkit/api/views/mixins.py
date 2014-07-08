# -*- coding: UTF-8 -*-
"""
Matter resolver Mixins
"""
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.renderers import JSONRenderer
from rest_framework.status import is_success

from toolkit.core.item.models import Item
from toolkit.apps.discussion.models import DiscussionComment
from toolkit.apps.workspace.models import Workspace

import logging
logger = logging.getLogger('django.request')


class _MetaJSONRendererMixin(JSONRenderer):
    """
    Mixin to append a _meta object at the root of the default json response
    which then contains everything that is accesssd via self.get_meta(self)
    """
    def get_meta(self):
        raise NotImplementedError

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is not None:
            #
            # Update with out meta object
            # but only when its a 2* response
            #
            if is_success(renderer_context.get('view').response.status_code) is True:
                get_meta_method = getattr(renderer_context.get('view'), 'get_meta', None)

                if get_meta_method is None:
                    logger.error('_MetaJSONRendererMixin.get_meta_method requires the view to define a .get_meta method')
                    raise Exception('_MetaJSONRendererMixin requires the calling view to have a .get_meta(self) method defined')

                data.update({
                    '_meta': get_meta_method() if get_meta_method is not None else None
                })

        return super(_MetaJSONRendererMixin, self).render(data=data,
                                                      accepted_media_type=accepted_media_type,
                                                      renderer_context=renderer_context)


class MatterMixin(generics.GenericAPIView):
    """
    Get the matter from the url slug :matter_slug
    """
    def initialize_request(self, request, *args, **kwargs):
        # provide the matter object
        self.matter = get_object_or_404(Workspace, slug=kwargs.get('matter_slug'))
        return super(MatterMixin, self).initialize_request(request, *args, **kwargs)


class MatterItemsQuerySetMixin(MatterMixin):
    """
    Mixin to filter the Items objects by their matter via the url :matter_slug
    """
    def get_queryset(self):
        return Item.objects.filter(matter=self.matter)


class SpecificAttributeMixin(object):
    """
    mixin to allow use of specific attribute mixin
    """
    specific_attribute = None

    def __init__(self, *args, **kwargs):
        if self.specific_attribute is None:
            raise Exception('You must define a self.specific_attribute attrib that exists on the object')

        super(SpecificAttributeMixin, self).__init__(*args, **kwargs)

    def get_object(self):
        self.object = super(SpecificAttributeMixin, self).get_object()
        return getattr(self.object, self.specific_attribute, None)


class ThreadMixin(MatterMixin, generics.GenericAPIView):
    """
    Get the thread from the url slug :thread_slug
    """
    def initialize_request(self, request, *args, **kwargs):
        request = super(ThreadMixin, self).initialize_request(request, *args, **kwargs)

        # provide the thread object
        self.thread = get_object_or_404(DiscussionComment.objects.for_model(self.matter), slug=kwargs.get('thread_slug'))
        return request
