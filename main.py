from typing import Literal

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.models import Lead, LeadResponse, LeadDBResponse
from app.services import analyze_lead
from app.database import Base, engine, get_db
from app import db_models
from app.db_models import LeadDB


Base.metadata.create_all(bind=engine)


app = FastAPI()


@app.get("/")
def home():
    return {"message": "SmartLead AI działa!"}


@app.post("/leads", response_model=LeadResponse)
def create_lead(lead: Lead, db: Session = Depends(get_db)):
    analysis = analyze_lead(lead.message)

    lead_db = LeadDB(
        name=lead.name,
        email=str(lead.email),
        message=lead.message,
        category=analysis.category,
        priority=analysis.priority
    )

    db.add(lead_db)
    db.commit()
    db.refresh(lead_db)

    return {
        "message": "Dane klienta zostały odebrane.",
        "lead": lead,
        "analysis": analysis
    }
    
    
@app.get("/leads", response_model=list[LeadDBResponse])
def get_leads(
    priority: Literal["normal", "high"] | None = None,
    category: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(LeadDB)

    if priority:
         query = query.filter(LeadDB.priority == priority)

    if category:
        query = query.filter(LeadDB.category == category)

    return query.all()