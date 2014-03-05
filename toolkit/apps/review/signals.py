# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed

from .models import ReviewDocument


@receiver(m2m_changed, sender=ReviewDocument.reviewers.through)
def on_reviewer_add(sender, instance, action, **kwargs):
    """
    when a reviewer is added from the m2m then authorise them
    for access
    """
    if action in ['post_add']:
        # get User
        user = User.objects.filter(pk__in=kwargs.get('pk_set')).first()
        instance.authorise_user_to_review(user=user)


@receiver(m2m_changed, sender=ReviewDocument.reviewers.through)
def on_reviewer_remove(sender, instance, action, **kwargs):
    """
    when a reviewer is removed from the m2m then deauthorise them
    """
    if action in ['post_remove']:
        # get user
        user = User.objects.filter(pk__in=kwargs.get('pk_set')).first()
        instance.deauthorise_user_to_review(user=user)
