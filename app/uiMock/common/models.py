# -*- coding: utf-8 -*-
from django.db import models
from django.contrib import admin
import django.utils.timezone as timezone

# Create your models here.
class ActionResponse(models.Model):
    action = models.TextField(u'请求')
    request = models.TextField(u'请求内容')
    request_header = models.TextField(u'请求头')
    response = models.TextField(u'响应内容')
    response_header = models.TextField(u'响应头')
    status_step = models.IntegerField(u'状态',default=0)

    def __unicode__(self):
        return self.action

class ActionResponseAdmin(admin.ModelAdmin):
    list_display = ('action','status_step','request_header')
    search_fields = ('action',)
    list_filter = ('action',)

class ActionLogs(models.Model):
    action = models.TextField(u'请求')
    request_header = models.TextField(u'请求头')
    request = models.TextField(u'请求内容')
    response_header = models.TextField(u'响应头')
    response = models.TextField(u'响应内容')
    actiontime = models.DateTimeField(u'请求时间',default=timezone.now)

admin.site.register(ActionResponse,ActionResponseAdmin)
