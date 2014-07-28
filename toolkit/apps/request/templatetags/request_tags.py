# -*- coding: UTF-8 -*-
from django import template
from django.core.urlresolvers import reverse


register = template.Library()


@register.inclusion_tag('request/request_list_review.html', takes_context=False)
def request_reviews_section(object_list, user):
    return {
        'object_list': [item for item in object_list.get('items', []) if item.needs_review(user)],
        'user': user
    }


@register.inclusion_tag('request/request_list_review_item.html', takes_context=False)
def request_review_item(item, user):
    review = None
    approval_url = None
    review_url = None
    if item.latest_revision:
        review = item.latest_revision.reviewdocument_set.filter(reviewers=user).first()
        approval_url = review.get_approval_url(user) if review else None
        review_url = review.get_absolute_url(user) if review else None
    return {
        'approve_url': approval_url,
        'item': item,
        'review': review,
        'review_url': review_url,
        'user': user
    }


@register.inclusion_tag('request/request_list_signing.html', takes_context=False)
def request_signings_section(object_list, user):
    return {
        'object_list': [item for item in object_list.get('items', []) if item.needs_signature(user)],
        'user': user
    }


@register.inclusion_tag('request/request_list_signing_item.html', takes_context=False)
def request_signing_item(item, user):
    return {
        'item': item,
        'signing_url': None,
        'user': user
    }


@register.inclusion_tag('request/request_list_upload.html', takes_context=False)
def request_uploads_section(object_list, user):
    return {
        'object_list': [item for item in object_list.get('items', []) if item.needs_upload(user)],
        'user': user
    }

@register.inclusion_tag('request/request_list_upload_item.html', takes_context=False)
def request_upload_item(item, user):
    return {
        'item': item,
        'upload_url': reverse('matter_item_revision', kwargs={'matter_slug': item.matter.slug, 'item_slug': item.slug}),
        'user': user
    }


@register.inclusion_tag('request/request_list_task.html', takes_context=False)
def request_tasks_section(object_list, user):
    return {
        'object_list': object_list.get('tasks', []),
        'user': user
    }

@register.inclusion_tag('request/request_list_task_item.html', takes_context=False)
def request_task_item(task, user):
    item = task.item
    return {
        'item': item,
        'task': task,
        'mark_as_complete_url': reverse('item_task', kwargs={'matter_slug': item.matter.slug, 'item_slug': item.slug, 'slug': task.slug}),
        'user': user
    }


@register.inclusion_tag('request/request_list_signing_has_signed.html', takes_context=False)
def user_has_signed(item, user):
    base = {
            'user_has_signed': None,
            'sign_url': None,
            'is_claimed': None,
            'requested_by': None,
        }
    if item.latest_revision:
        sign_document = item.latest_revision.primary_signdocument

        base.update({
            'user_has_signed': sign_document.has_signed(signer=user),
            'sign_url': sign_document.get_absolute_url(signer=user),
            'is_claimed': sign_document.signing_request.is_claimed if sign_document.signing_request is not None else None,
            'requested_by': sign_document.requested_by,
        })
    return base
