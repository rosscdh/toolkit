# -*- coding: utf-8 -*-
from toolkit.api.serializers import ItemSerializer
from toolkit.api.serializers.user import LiteUserSerializer
from toolkit.core.signals import send_activity_log

from abridge.services import AbridgeService


class LawPalAbridgeService(object):
    """
    Wrapper for wrapping the abridge service
    allows us to disable it in testing and based on settings
    """
    ABRIDGE_ENABLED = False
    service = None

    def __init__(self, user, ABRIDGE_ENABLED=False, **kwargs):
        self.ABRIDGE_ENABLED = ABRIDGE_ENABLED

        assert user.__class__.__name == 'User', 'user must be a auth.User object'

        self.service = None  # reset to None by default
        if self.ABRIDGE_ENABLED:  # check if enabled
            self.service = AbridgeService(user=user)

    def create_event(self, content_group, content, **kwargs):
        if self.service is not None and self.ABRIDGE_ENABLED is True:
            self.service.create_event(content_group=content_group,
                                      content=content)


class MatterActivityEventService(object):
    def __init__(self, matter, **kwargs):
        self.matter = matter

    def _create_activity(self, actor, verb, action_object, **kwargs):
        activity_kwargs = {
            'actor': actor,
            'verb': verb,
            'action_object': action_object,
            'target': self.matter,
            'message': kwargs.get('message', None),
            'user': None if not kwargs.get('user', None) else LiteUserSerializer(kwargs.get('user', None)).data,
            'item': None if not kwargs.get('item', None) else ItemSerializer(kwargs.get('item', None)).data,
        }
        send_activity_log.send(self, **activity_kwargs)

    def created_matter(self, lawyer):
        self.create_activity(actor=lawyer, verb=u'created', action_object=self.matter)

    def created_item(self, user, item):
        self.create_activity(actor=user, verb=u'created', action_object=item)

    def created_revision(self, user, item, revision):
        message = u'%s created a revision for %s' % (user, item)
        self.create_activity(actor=user, verb=u'created', action_object=revision, item=item, message=message)

    def deleted_revision(self, user, item, revision):
        message = u'%s destroyed a revision for %s' % (user, item)
        self.create_activity(actor=user, verb=u'deleted', action_object=revision, item=item, message=message)

    def added_user_as_reviewer(self, item, adding_user, added_user):
        message = u'%s added %s as reviewer for %s' % (adding_user, added_user, item)
        self.create_activity(actor=adding_user, verb=u'edited', action_object=item, message=message,
                             user=added_user)

    def removed_user_as_reviewer(self, item, removing_user, removed_user):
        message = u'%s removed %s as reviewer for %s' % (removing_user, removed_user, item)
        self._create_activity(actor=removing_user, verb=u'edited', action_object=item, message=message,
                             user=removed_user)
