from leads_agregator.exceptions.agregator_exceptions import NoNewLeads
from web.app.models import *
from tgbot.schemas.lead import Lead as LeadSchema

def get_or_create_worker(**kwargs):
    return Worker.objects.get_or_create(**kwargs)

def is_worker_exists_sync(**kwargs):
    return Worker.objects.filter(**kwargs).exists()

def get_worker(**kwargs):
    return Worker.objects.get(**kwargs)

def delete_worker_sync(**kwargs):
    worker = Worker.objects.get(**kwargs)
    worker.delete()
    return worker

def stop_or_activate_worker_sync(**kwargs):
    worker: Worker = Worker.objects.get(**kwargs)
    worker.stop = not worker.stop
    worker.save()
    return worker

def get_all_workers():
    return list(Worker.objects.all())

def get_active_workers():
    return list(
        Worker.objects.filter(stop=False)\
            .order_by('id')\
                .values_list('telegram_id', flat=True)
        )
    
def get_next_worker_telegram_id(previous_worker_telegram_id):
    worker = Worker.objects.get(telegram_id=previous_worker_telegram_id)
    if len(get_active_workers()) < 2:
        return str(None)
    if workern := Worker.objects.filter(
        id__lt=worker.id,
        stop=False,
        ).order_by('id').last():
        return workern.telegram_id
    else:
        return Worker.objects.filter(
            id__gt=worker.id,
            stop=False,
        ).order_by('id').first().telegram_id

def get_new_leads() -> list[LeadSchema]:
    if not Lead.objects.filter(is_new=True).exists():
        raise NoNewLeads
    return list(
        LeadSchema(
            id=lead.id,
            created_time=lead.created_time,
            name=lead.name,
            phone=lead.phone,
            campaign_name=lead.campaign_name,
            ad_name=lead.ad_name,
            adset_name=lead.adset_name,
            platform=lead.platform,
            )
        for lead in Lead.objects.filter(is_new=True)
        )
            
def update_lead_is_new_status(lead_id: int):
    lead: Lead = Lead.objects.get(id=lead_id)
    lead.is_new = False
    lead.save()