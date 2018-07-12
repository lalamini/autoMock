from django.shortcuts import render
from django.http import HttpResponse
import common.public
import logging
import sys
defaultencoding = 'utf-8'

if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

logger = logging.getLogger("django")

# Create your views here.


def api_proxy(request):
    logger.debug("get response functio")
    result = common.public.get_http_response(request)
    response = HttpResponse()
    ddd = result['header']
    for key in ddd:
        response[key] = ddd[key]
    response.content = result['content']
    return response

