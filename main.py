from typing import Literal

from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.models import Lead, LeadResponse, LeadDBResponse, LeadUpdate, LeadStats
from app.services import analyze_lead, prepare_lead_update
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
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(LeadDB)

    if priority:
         query = query.filter(LeadDB.priority == priority)

    if category:
        query = query.filter(LeadDB.category == category)

    query = query.offset(offset).limit(limit)

    return query.all()


@app.get("/stats", response_model=LeadStats)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(LeadDB).count()

    high_priority = (
        db.query(LeadDB)
        .filter(LeadDB.priority == "high")
        .count()
    )

    normal_priority = (
        db.query(LeadDB)
        .filter(LeadDB.priority == "normal")
        .count()
    )

    return {
        "total": total,
        "high_priority": high_priority,
        "normal_priority": normal_priority
    }


@app.get("/leads/{lead_id}", response_model=LeadDBResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead nie został znaleziony"
        )

    return lead


@app.get("/leads/{lead_id}", response_model=LeadDBResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()

    if not lead:
        return {"detail": "Lead nie został znaleziony"}

    return lead


@app.get("/leads/{lead_id}", response_model=LeadDBResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead nie został znaleziony"
        )

    return lead


@app.delete("/leads/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead nie został znaleziony"
        )

    db.delete(lead)
    db.commit()

    return {"message": "Lead został usunięty"}


@app.put("/leads/{lead_id}", response_model=LeadDBResponse)
def update_lead(
    lead_id: int,
    lead: LeadUpdate,
    db: Session = Depends(get_db)
):
    existing_lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()

    if not existing_lead:
        raise HTTPException(
            status_code=404,
            detail="Lead nie został znaleziony"
        )

    prepare_lead_update(lead, existing_lead)

    db.commit()
    db.refresh(existing_lead)

    return existing_lead