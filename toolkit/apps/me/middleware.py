# -*- coding: utf-8 -*-
from django.contrib import messages
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

import logging
logger = logging.getLogger('django.request')


class EnsureUserHasPasswordMiddleware(object):
    """ ensure that the current user has set their password
    if they have not then redirect them to the password page
    """
    def process_request(self, request):
        if request.user.is_authenticated():
            #
            # cater to the various version '' '!' and None deal with various versions
            # of empty passwords
            #
            if request.user.password in ['', '!', None]:
                if request.get_full_path() not in [reverse('public:logout'),
                                                   reverse('me:settings'),
                                                   reverse('me:confirm-account'),
                                                   reverse('me:change-password')] \
                    and '/review/' not in request.get_full_path():
                    logger.info('User has not set their password: %s will redirect to me:settings' % request.user)
                    messages.error(request, 'Please enter a Password and confirm your Email address, so that you can sign in.')
                    return redirect(reverse('me:confirm-account'))
        return None