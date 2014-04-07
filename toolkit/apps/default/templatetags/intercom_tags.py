import hmac, hashlib

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def intercom_user_hash(email):
    """
    Generate the user_hash to turn on secure mode for Intercom.
    """
    return hmac.new(settings.INTERCOM_API_SECRET, email, digestmod=hashlib.sha256).hexdigest()
