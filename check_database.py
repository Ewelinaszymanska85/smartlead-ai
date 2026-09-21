from sqlalchemy import select

from app.database import SessionLocal
from app.db_models import LeadDB


db = SessionLocal()

try:
    leads = db.scalars(select(LeadDB)).all()

    for lead in leads:
        print(
            lead.id,
            lead.name,
            lead.email,
            lead.category,
            lead.priority
        )
finally:
    db.close()