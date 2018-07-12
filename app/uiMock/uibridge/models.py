from django.db import models

# Create your models here.
# just record
class ActionStatusRecorder(models.Model):
    action = models.TextField(u'状态名')
    step = models.IntegerField(u'状态',default=0)
