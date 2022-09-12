from tgbot.schemas.lead import Lead as LeadSchema
from web.app.models import Lead as LeadORM

def write_leads_to_db(leads: list[LeadSchema]):
    for lead in leads:
        lead_orm = LeadORM(
            id=lead.id,
            form_id=lead.form_id,
            created_time=lead.created_time,
            name=lead.name,
            phone=lead.phone,
            )
        lead_orm.save()