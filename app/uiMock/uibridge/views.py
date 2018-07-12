# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
import re
import common.public
from uiMock import configuration as c
import logging
try:
    import urllib2 as urlrequest
except ImportError:
    import urllib.request as urlrequest
    from urllib import error
import collections
import json
import ssl
import sys

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)


ssl._create_default_https_context = ssl._create_unverified_context

# Create your views here.
logger = logging.getLogger("django")
def api_bridge(request):
    regex = re.compile('^HTTP_') 
    result = dict((regex.sub('', header), value) for (header, value) in request.META.items() if header.startswith('HTTP_'))
    logger.debug("origin host dest is:"+result['HOST'])
    full_path = request.get_full_path()
    re_result = [re.search(a,result['HOST']) for a in c.HTTPS_RE_MATCH] 
    #use http or https according to HTTPS_RE_MATCH list
    request_path = "http://"
    for a_tmp in re_result:
        if a_tmp:
            request_path = "https://"
    request_path += result["HOST"]  + full_path
    logger.debug(request_path)
    #to form a request via urlrequest.Request function
    sql_request_body = ""
    if request.body:
        req = urlrequest.Request(request_path,request.body)
        sql_request_body += request.body.decode()
    else:
        req = urlrequest.Request(request_path)
    #use OrderedDict to store the request_header hash , make the sql match
    sql_request_header  = collections.OrderedDict()
    for key in result:
        sql_request_header[key] = result[key]
        req.add_header(key , result[key])
    #send the request to origin host
    try:
        respon = urlrequest.urlopen(req)
    except error.URLError as e:
        response = HttpResponse()
        response.content = e.reason
        logger.warning(e.reason)
        return response
    header_hash = respon.getheaders()
    response = HttpResponse()
    #use OrderedDict to store the reponse_header hash , make the sql match
    sql_response_header = collections.OrderedDict()
    for value in header_hash:
        sql_response_header[value[0]] = value[1] #the hash header stored into mysql
        response[value[0]]  = value[1]  #the response structure , header

    response.content = respon.read()
    sql_response_content = ""
    sql_response_content += response.content.decode()
    #some key in request header is not needed, such as timestamp and so on
    clean_sql_request_header = common.public.remove_req_header_key(sql_request_header)
    keys = sorted(clean_sql_request_header.keys())
    json_str = "{"
    for key in keys:
        json_str += '"'+key+'":"'+clean_sql_request_header[key] +'",'
    json_str = json_str[:-1]
    json_str += "}"
    #some key in response header is not needed, such as timestamp and so on
    finial_response_header = common.public.remove_req_header_key(sql_response_header)
    result = common.public.save_request_response(full_path,json_str,sql_request_body,json.dumps(finial_response_header),sql_response_content)
    return response
