import hmac, hashlib

from django import template
from django.conf import settings

register = template.Library()


def _get_intercom_user_hash(user_identifier):
    return hmac.new(settings.INTERCOM_APP_SECRET, user_identifier, digestmod=hashlib.sha256).hexdigest()


@register.simple_tag
def intercom_user_hash(username):
    """
    Generate the user_hash to turn on secure mode for Intercom.
    """
    return _get_intercom_user_hash(user_identifier=username)
