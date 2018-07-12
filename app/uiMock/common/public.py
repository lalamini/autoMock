# -*- coding=UTF-8 -*-
import zlib
import gzip
import json
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import io
#from django.db import connection,transaction
#from recordmanager.models import ActionResponse,ActionLogs,ActionStatusRecorder,ActionCurrentStatus
from uibridge.models import ActionStatusRecorder
from .models import ActionResponse
from uiproxy.models import ActionCurrentStatus
import collections
import re
from uiMock import configuration as c
import logging
import sys

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)


logger = logging.getLogger("django")


def save_request_response(action,reqh,reqb,reph,repc):
    print ("save request and response function, action is",action)
    logger.debug("save request and response function, action is %s",[action])
    a_string = action
    index = a_string.rfind(r"?")
    logger.debug("index %s",[index])
    if index != -1:
        a_string = a_string[:index]
    logger.debug("a_string is %s",[a_string])
    operations = []
    action_strings = []
    status_node_names = []
    #print ("save request and response function, reqh is",reqh)
    #print ("save request and response function, reqb is",reqb)
    #print ("save request and response function, reph is",reph)
    #print ("save request and response function, repc is",repc.encode())
    #if the action will affect the node status , may be one action will effect two status_node ,so we will have a list
    for node in c.STATUS_NODE:
        for status_node_name, value in node.items(): #this key is status_node
            for k,v in value.items():
                if a_string  == k:
                    #get status code from key column
                    action_strings.append(a_string)
                    operations.append(v)
                    status_node_names.append(status_node_name)
    logger.debug("action_string is %s",[action_strings])
    for i in  range(len(action_strings)):
        action_string = action_strings[i]
        operation = operations[i]
        status_node_name = status_node_names[i]
        #has action_string
        if action_string and operation != 'r':#operation has action
            logger.debug("do effect on %s",[status_node_name])
            try:
                obj = ActionStatusRecorder.objects.get(action=status_node_name) #do step + 1 to restore
                logger.debug("StatusRecorder's get step is: %s",[obj.step])
                exec ("obj.step "+operation+"=1")
                #obj.step += 1
            except ActionStatusRecorder.DoesNotExist:
                logger.debug("StatusRecorder's no step , create one")
                obj = ActionStatusRecorder.objects.create(action=status_node_name,step=1)
            obj.save()
            step = obj.step
        elif action_string and operation == 'r':#operation just read
            logger.debug("StatusRecorder's no effect ,but use on %s",[status_node_name])
            try:
                obj = ActionStatusRecorder.objects.get(action=status_node_name)
                step = obj.step
            except ActionStatusRecorder.DoesNotExist:
                logger.debug("StatusRecorder's not exist , just return step=0")
                step = 0
        else:#has no action_string
            logger.debug("all else is step=0")
            step = 0

        if operation == 'r':
            logger.debug("log action response and set the setep=%s",[step])
            ActionResponse.objects.create(action=action,request=reqb,request_header=reqh,response=repc,response_header=reph,status_step=step)
        else:
            logger.debug("log new action response and set the setep=0")
            ActionResponse.objects.create(action=action,request=reqb,request_header=reqh,response=repc,response_header=reph,status_step=0)
    if len(action_strings) == 0:
        logger.debug("log new action when no effect on status_node, create one that step=0")
        ActionResponse.objects.create(action=action,request=reqb,request_header=reqh,response=repc,response_header=reph,status_step=0)

    return

def gzip_compress(string):
    gzip_compress = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
    gzip_data = gzip_compress.compress(string)  + gzip_compress.flush()
    return gzip_data

def get_response(action,reqh,reqbody):
    print ("get response function, action is",action)
    logger.debug("get response function, action is %s",[action])
    a_string = action
    index = a_string.rfind(r"?")
    if index != -1:
        a_string = a_string[:index]
    operations = []
    action_strings = []
    status_node_names = []
    if action in c.NEED_REQUESTBODY:
        need_reqbody = 1
    else:
        need_reqbody = 0
    for node in c.STATUS_NODE:
        for status_node_name, value in node.items(): #this key is status_node
            for k,v in value.items():
                if a_string  == k:
                    #get status code from key column
                    action_strings.append(a_string)
                    operations.append(v)
                    status_node_names.append(status_node_name)
    for i in  range(len(action_strings)): #if the action is in the status_node list
        action_string = action_strings[i]
        operation = operations[i]
        status_node_name = status_node_names[i]
        if action_string and operation != 'r':
            logger.debug("has operaion effect")
            try:
                obj = ActionCurrentStatus.objects.get(action=status_node_name)
                logger.debug("action exist")
                exec ("obj.step "+operation+"=1")
                #obj.step += 1
            except ActionCurrentStatus.DoesNotExist:
                logger.debug("action not exist")
                obj = ActionCurrentStatus.objects.create(action=status_node_name,step=1)
            obj.save()
            step = obj.step
            if need_reqbody == 0:
                qs = ActionResponse.objects.filter(action=action).filter(status_step=0).filter(request_header=reqh).order_by('-id')[0]
            else:
                qs = ActionResponse.objects.filter(action=action).filter(status_step=0).filter(request_header=reqh).filter(request=reqbody.decode()).order_by('-id')[0]
        else:
            try:
                logger.debug("has no operation effect and exist")
                obj = ActionCurrentStatus.objects.get(action=status_node_name)
                step = obj.step
            except ActionCurrentStatus.DoesNotExist:
                logger.debug("has no operation effect and not exist")
                step = 0
            if need_reqbody == 0:
                qs = ActionResponse.objects.filter(action=action).filter(status_step=step).filter(request_header=reqh).order_by('-id')[0]
            else:
                qs = ActionResponse.objects.filter(action=action).filter(status_step=step).filter(request_header=reqh).filter(request=reqbody.decode()).order_by('-id')[0]
    if len(action_strings) == 0:#if the action is not in the status_node list
        step = 0
        if need_reqbody == 0:
            qs = ActionResponse.objects.filter(action=action).filter(status_step=step).filter(request_header=reqh).order_by('-id')[0]
        else:
            logger.debug("action_string != 0 and need req body")
            qs = ActionResponse.objects.filter(action=action).filter(status_step=step).filter(request_header=reqh).filter(request=reqbody.decode()).order_by('-id')[0]
    result = {}
    result['header'] = json.loads(qs.response_header)
    result['content'] = qs.response
    return result

def remove_req_header_key(req):
    result = collections.OrderedDict()
    for key in req:
        if key not in c.REMOVE_REQUEST_HEAD_KEY:
            result[key] = req[key]
    return result

def get_http_response(request):
    regex = re.compile('^HTTP_')
    header = dict((regex.sub('', header), value) for (header, value) in request.META.items() if header.startswith('HTTP_'))
    full_path = request.get_full_path()
    sql_request_header = collections.OrderedDict()
    sql_request_header = remove_req_header_key(header)
    keys = sorted(sql_request_header.keys())
    json_str = "{"
    for key in keys:
        json_str += '"'+key+'":"'+sql_request_header[key] +'",'
    json_str = json_str[:-1]
    json_str += "}"
    result = get_response(full_path,json_str,request.body)
    return result
