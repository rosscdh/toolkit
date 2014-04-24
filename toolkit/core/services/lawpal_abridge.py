# -*- coding: utf-8 -*-
from abridge.services import AbridgeService
from django import template
from toolkit.apps.notification.templatetags.notice_tags import get_notification_template, get_notification_context


class LawPalAbridgeService(object):
    """
    Wrapper for wrapping the abridge service
    allows us to disable it in testing and based on settings
    """
    ABRIDGE_ENABLED = False
    service = None

    def __init__(self, user, ABRIDGE_ENABLED=False, **kwargs):
        self.ABRIDGE_ENABLED = ABRIDGE_ENABLED

        assert user.__class__.__name__ == 'User', 'user must be a auth.User object'

        self.service = None  # reset to None by default
        if self.ABRIDGE_ENABLED:  # check if enabled
            self.service = AbridgeService(user=user)

    def create_event(self, content_group, content, **kwargs):
        if self.service is not None and self.ABRIDGE_ENABLED is True:
            self.service.create_event(content_group=content_group,
                                      content=content)

    @classmethod
    def render_message_template(cls, user, **kwargs):
        verb_slug = kwargs.pop('verb_slug')
        message = kwargs.pop('message')

        t = get_notification_template(verb_slug)
        ctx = get_notification_context(kwargs, user)
        ctx.update({
            # 'notice_pk': notice.pk,
            # 'date': notice.message.date,
            'message': message,
        })

        context = template.loader.Context(ctx)
        return t.render(context)