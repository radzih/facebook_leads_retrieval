from django.contrib import admin

from web.app.models import Worker
# Register your models here.

class WorkerAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'name', 'position', 'stop')
    
admin.site.register(Worker, WorkerAdmin)