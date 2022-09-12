from platform import platform
from tgbot.schemas.lead import Lead as LeadSchema
from web.app.models import Lead as LeadORM

def write_leads_to_db(leads: list[LeadSchema]):
    for lead in leads:
        lead_orm = LeadORM(
            **lead.dict()
            )
        lead_orm.save()