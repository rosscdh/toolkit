import hmac, hashlib

from django import template
from django.conf import settings

register = template.Library()


def _get_intercom_user_hash(user_identifier):
    """
    user_identifier should be user.pk, have implemented like this as at this time
    we are using email which is wrong waiting on jamies api fix to set the user_id 
    at intercom
    @TODO check this with J and make sure weve set the user_id at intercom
    then change user_identifier to be user.pk
    """
    return hmac.new(settings.INTERCOM_APP_SECRET, user_identifier, digestmod=hashlib.sha256).hexdigest()


@register.simple_tag
def intercom_user_hash(email):
    """
    Generate the user_hash to turn on secure mode for Intercom.
    """
    return _get_intercom_user_hash(user_identifier=email)
