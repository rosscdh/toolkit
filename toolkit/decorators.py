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
