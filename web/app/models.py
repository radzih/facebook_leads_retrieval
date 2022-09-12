from platform import platform
from django.db import models

# Create your models here.

class Worker(models.Model):
    class Meta:
        db_table = 'workers'
        
    telegram_id: int = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    stop = models.BooleanField(default=False)
    
class Lead(models.Model):
    class Meta:
        db_table = 'leads'
        
    id = models.BigIntegerField(primary_key=True)
    created_time = models.DateTimeField()
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=14)
    is_new = models.BooleanField(default=True)
    campaign_name = models.CharField(max_length=255)
    ad_name = models.CharField(max_length=255)
    adset_name = models.CharField(max_length=255)
    platform = models.CharField(max_length=255)