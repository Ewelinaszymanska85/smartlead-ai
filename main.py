from datetime import date, timedelta

from typing import Literal

from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.models import (
    Lead,
    LeadResponse,
    LeadDBResponse,
    LeadUpdate,
    LeadStats,
    LeadStatusUpdate,
    UserCreate
)
from app.services import analyze_lead, prepare_lead_update
from app.security import hash_password
from app.database import Base, engine, get_db
from app import db_models
from app import user_models
from app.user_models import UserDB
from app.db_models import LeadDB


Base.metadata.create_all(bind=engine)


app = FastAPI()


@app.get("/")
def home():
    return {"message": "SmartLead AI działa!"}


@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    password_hash = hash_password(user.password)

    new_user = UserDB(
        username=user.username,
        password_hash=password_hash
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Użytkownik został utworzony",
        "username": new_user.username
    }


@app.post("/leads", response_model=LeadResponse)
def create_lead(lead: Lead, db: Session = Depends(get_db)):
    analysis = analyze_lead(lead.message)

    lead_db = LeadDB(
        name=lead.name,
        email=str(lead.email),
        message=lead.message,
        category=analysis.category,
        priority=analysis.priority,
        status="new"
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
    category: Literal[
        "sklep internetowy",
        "aplikacja mobilna",
        "strona internetowa",
        "inne"
    ] | None = None,
    search: str | None = Query(None, min_length=2),
    sort: Literal["newest", "oldest"] | None = None,
    created_from: date | None = None,
    created_to: date | None = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(LeadDB)
    
    if created_from and created_to and created_from > created_to:
        raise HTTPException(
            status_code=422,
            detail="Data początkowa nie może być późniejsza niż data końcowa"
        )

    if priority:
        query = query.filter(LeadDB.priority == priority)

    if category:
        query = query.filter(LeadDB.category == category)
        
    if created_from:
        query = query.filter(LeadDB.created_at >= created_from)
        
    if created_to:
        created_to_next_day = created_to + timedelta(days=1)
        query = query.filter(LeadDB.created_at < created_to_next_day)

    if search:
        query = query.filter(
            LeadDB.name.ilike(f"%{search}%")
            | LeadDB.email.ilike(f"%{search}%")
            | LeadDB.message.ilike(f"%{search}%")
        )

    if sort == "newest":
        query = query.order_by(LeadDB.id.desc())
    elif sort == "oldest":
        query = query.order_by(LeadDB.id.asc())

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

    categories = {}

    for category in db.query(LeadDB.category).distinct():
        category_name = category[0]

        categories[category_name] = (
            db.query(LeadDB)
            .filter(LeadDB.category == category_name)
            .count()
        )

    return {
        "total": total,
        "high_priority": high_priority,
        "normal_priority": normal_priority,
        "categories": categories
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

@app.patch("/leads/{lead_id}/status", response_model=LeadDBResponse)
def update_lead_status(
    lead_id: int,
    status_update: LeadStatusUpdate,
    db: Session = Depends(get_db)
):
    lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead nie został znaleziony"
        )

    lead.status = status_update.status

    db.commit()
    db.refresh(lead)

    return lead