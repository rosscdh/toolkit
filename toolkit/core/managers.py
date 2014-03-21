# -*- coding: utf-8 -*-
from actstream.managers import ActionManager, stream
import datetime
from toolkit.core.mixins import IsDeletedManager


class ToolkitActionManager(IsDeletedManager, ActionManager):

    @stream
    def target_by_customer_stream(self, object, customer, **kwargs):
        # TODO get information since when customer may see action and include here:
        time_start = datetime.datetime.now() - datetime.timedelta(seconds=1)

        kwargs.update({
            'timestamp__gte': time_start,
        })
        return object.target_actions.public(**kwargs)

    @stream
    def action_object_by_customer_stream(self, object, customer, **kwargs):
        # TODO get information since when customer may see action and include here:
        time_start = datetime.datetime.now() - datetime.timedelta(seconds=1)

        kwargs.update({
            'timestamp__gte': time_start,
        })
        return object.action_object_actions.public(**kwargs)