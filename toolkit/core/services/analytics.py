# -*- coding: utf-8 -*-
from django.conf import settings
from mixpanel import Mixpanel, MixpanelException

import logging
logger = logging.getLogger('django.request')


MIXPANEL_SETTINGS = getattr(settings, 'MIXPANEL_SETTINGS', {
    'token': None,
})


class MixpanelOnLawpal(object):
    token = None
    service = None
    def __init__(self, *args, **kwargs):
        self.token = kwargs.get('token', MIXPANEL_SETTINGS.get('token', None))
        if self.token is not None:
            self.service = Mixpanel(self.token)

    def mixpanel_alias(self, alias_id, original, **kwargs):
        if self.service is not None:
            try:
                self.service.alias(alias_id=alias_id, original=original, **kwargs)
            except MixpanelException:
                logger.error('Mixpanel error: distinct_id, missing or empty: %s' % alias_id)

    def event(self, key, user, distinct_id=None, **kwargs):
        if self.service is not None:
            if distinct_id is None:
                distinct_id = user.pk

            all_properties = {
                'account_type': user.profile.account_type,
                'user': user.get_full_name(),
                'user_type': user.profile.type,
                'via': 'web'
            }
            all_properties.update(kwargs)

            self.service.track(distinct_id=distinct_id, event_name=key, properties=kwargs)


class AtticusFinch(MixpanelOnLawpal):
    """
    http://www.imdb.com/title/tt0056592/
    Abstraction class used to implement 1 of the potential analytics services;
    """
    pass


#
# KeenIO - evaluated was not up toscratch
# but did provide a nice way of exposing the data to customers perhaps in the future
#
#import keen
#
# KEEN_SETTINGS = {
#     'project_id': '533729cad97b8563aa000018',
#     'write_key': '034de182e7c9bde121e37d69132fe5c183292dba5f54f694f2ce0f4ea87107f95b1db6358eb1959bac99fbb8243a119a2b8e736864fb1e6d152c86eb37a19638c41112f0e65f3f651ec8437d172f054cef12da875928a0e9a83b4c3787a692744eac4a3d27cc97a11eda2936c92ceff8',
#     'read_key': 'efd47a6e7475489958881e810faa71d3013ea5824610d551734dcb12ee6533e7a51655f2f39db60680443d5a1f27a3436e15fbdb6d0b1e9f921db835d7b70886fa5206edbbd99a6388283bbcc4bab4d3a9858a6e219e80bc2316de505529dc3d7bd44546cc15c257f4c5a8af45fba050',
# }

# KEEN_SETTINGS = getattr(settings, 'KEEN_SETTINGS', {
#     'project_id': None,
#     'write_key': None,
#     'read_key': None,
# })
# class KeenIOOnLawpal(object):
#     """
#     Keen is useful to us because it allows us to expose viaulizations to the end user
#     """
#
#     def __init__(self, *args, **kwargs):
#         keen.project_id = KEEN_SETTINGS.get('project_id', kwargs.get('project_id', None))
#         keen.write_key = KEEN_SETTINGS.get('write_key', kwargs.get('write_key', None))
#         keen.read_key = KEEN_SETTINGS.get('read_key', kwargs.get('read_key', None))

#     def event(self, key, **kwargs):
#         assert kwargs, 'event.kwargs must be defined'
#         assert len(kwargs.keys()) > 0, 'event.kwargs must have at least 1 {key: value} defined'
#         keen.add_event(key, kwargs)
