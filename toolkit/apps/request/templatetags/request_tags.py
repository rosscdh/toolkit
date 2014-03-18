# -*- coding: UTF-8 -*-
from django import template


register = template.Library()


@register.inclusion_tag('request/request_list_upload.html', takes_context=False)
def requests_upload_section(object_list, user):
    return {
        'object_list': object_list.needs_upload(user)
    }


@register.inclusion_tag('request/request_list_review.html', takes_context=False)
def requests_review_section(object_list, user):
    return {
        'object_list': object_list.needs_review(user),
    }


@register.inclusion_tag('request/request_list_signing.html', takes_context=False)
def requests_signing_section(object_list, user):
    return {
        'object_list': object_list.needs_signature(user),
    }
