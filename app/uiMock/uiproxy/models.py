from django.db import models

# Create your models here.
#regist the step
class ActionCurrentStatus(models.Model):
    action = models.TextField(u'状态名')
    step = models.IntegerField(u'目前状态',default=0)
