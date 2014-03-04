# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed

from .models import ReviewDocument

import base64
import hashlib


@receiver(m2m_changed, sender=ReviewDocument.reviewers.through)
def on_reviewer_add(sender, instance, action, **kwargs):
    """
    On the addition of a reviewer create a new auth object
    that consists of {
        ":random_slug_for_url": reviewer.pk
    }
    this is then used in the auth_backends.ReviewDocumentBackend
    """
    if action in ['post_add']:

        auth = instance.data.get('auth', {})
        user = User.objects.filter(pk__in=kwargs.get('pk_set')).first()

        if user.pk not in auth.values():
            hasher = hashlib.sha1('%s-%s' % (str(instance.slug), user.email))
            key = base64.urlsafe_b64encode(hasher.digest()[0:10])
            # set the auth
            auth.update({key: user.pk})

            instance.data['auth'] = auth
            instance.save(update_fields=['data'])



@receiver(m2m_changed, sender=ReviewDocument.reviewers.through)
def on_reviewer_remove(sender, instance, action, **kwargs):
    """
    On the removal of a reviewer remove the auth object
    that consists of {
        ":random_slug_for_url": reviewer.pk
    }
    this is then used in the auth_backends.ReviewDocumentBackend
    """
    if action in ['post_remove']:
        auth = instance.data.get('auth', {})
        user = User.objects.filter(pk__in=kwargs.get('pk_set')).first()
        if user.pk in auth.values():
            for key, value in auth.iteritems():
                if value == user.pk:
                    del auth[key]
                    break
            instance.data['auth'] = auth
            instance.save(update_fields=['data'])
