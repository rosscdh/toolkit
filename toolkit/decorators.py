from django.http import HttpResponseServerError
from django.utils import simplejson as json

from decorator import decorator


@decorator
def json_response(function=None, *args, **kwargs):
    try:
        response = function(*args, **kwargs)
    except Exception, e:
        error = {
            'error': {
                'message': unicode(e)
            }
        }
        response = HttpResponseServerError()
        response.content = json.dumps(error, separators=(',', ':'))

    response['Content-Type'] = 'application/json'
    return response


@decorator
def mutable_request(function, view, request, *args, **kwargs):
    """
    Make the django request.DATA and request.POST objects mutable to allow us
    to change and add and or remove values to the request object.
    @ANTIPATTERN
    see: https://stackoverflow.com/questions/12611345/django-why-is-the-request-post-object-immutable
    """
    if hasattr(request.DATA, '_mutable'):
        request.DATA._mutable = True
    if hasattr(request.POST, '_mutable'):
        request.POST._mutable = True

    return function(view, request, *args, **kwargs)