# -*- coding: UTF-8 -*-
from django import template
from django.core.urlresolvers import reverse


register = template.Library()


@register.inclusion_tag('request/request_list_review.html', takes_context=False)
def request_reviews_section(object_list, user):
    return {
        'object_list': object_list.needs_review(user),
        'user': user
    }


@register.inclusion_tag('request/request_list_review_item.html', takes_context=False)
def request_review_item(item, user):
    review = item.latest_revision.reviewdocument_set.filter(reviewers=user).first()

    return {
        'approve_url': review.get_approval_url(user),
        'item': item,
        'review': review,
        'review_url': review.get_absolute_url(user),
        'user': user
    }


@register.inclusion_tag('request/request_list_signing.html', takes_context=False)
def request_signings_section(object_list, user):
    return {
        'object_list': object_list.needs_signature(user),
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
        'object_list': object_list.needs_upload(user),
        'user': user
    }


@register.inclusion_tag('request/request_list_upload_item.html', takes_context=False)
def request_upload_item(item, user):
    return {
        'item': item,
        'upload_url': reverse('matter_item_revision', kwargs={'matter_slug': item.matter.slug, 'item_slug': item.slug}),
        'user': user
    }


@register.inclusion_tag('request/request_list_signing_has_signed.html', takes_context=False)
def user_has_signed(item, user):
    sign_document = item.latest_revision.primary_signdocument
    return {
        'user_has_signed': sign_document.has_signed(signer=user),
        'sign_url': sign_document.get_absolute_url(signer=user),
        'is_claimed': sign_document.signing_request.is_claimed,
        'requested_by': sign_document.requested_by,
    }
