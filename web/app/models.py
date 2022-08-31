from django.db import models

# Create your models here.

class Worker(models.Model):
    class Meta:
        db_table = 'worker'
        
    telegram_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    stop = models.BooleanField(default=False)