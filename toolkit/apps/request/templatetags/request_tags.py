# -*- coding: UTF-8 -*-
from django import template


register = template.Library()


@register.inclusion_tag('request/request_list_block.html', takes_context=False)
def requests_upload_section(object_list, user):
    return {
        'action_btn': u'Upload File',
        'description': u'Please upload the following documents:',
        'icon': 'fui-upload',
        'object_list': object_list.needs_upload(user),
        'story': u'requested you upload this document.',
        'title': u'Documents to be uploaded',
        'toggle': u'filepicker',
        'type': u'upload',
    }


@register.inclusion_tag('request/request_list_block.html', takes_context=False)
def requests_review_section(object_list, user):
    return {
        'action_btn': u'Review',
        'description': u'Please read and review the following documents:',
        'icon': 'fui-upload',
        'object_list': object_list.needs_review(user),
        'story': u'requested your feedback on this document',
        'title': u'Documents requiring review',
        'toggle': None,
        'type': u'review',
    }


@register.inclusion_tag('request/request_list_block.html', takes_context=False)
def requests_signing_section(object_list, user):
    return {
        'action_btn': u'Review and Sign',
        'description': u'Please read, review and sign the following documents:',
        'icon': 'fui-upload',
        'object_list': object_list.needs_signature(user),
        'story': u'requested your signature on this document.',
        'title': u'Documents to be signed',
        'toggle': None,
        'type': u'signing',
    }
