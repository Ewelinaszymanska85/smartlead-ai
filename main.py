from datetime import date, timedelta
from typing import Literal

from fastapi import FastAPI, Depends, Query, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.models import (
    Lead,
    LeadResponse,
    LeadDBResponse,
    LeadUpdate,
    LeadStats,
    LeadStatusUpdate,
    UserCreate,
    UserLogin,
    LeadNoteCreate
)
from app.services import analyze_lead, prepare_lead_update
from app.security import hash_password, verify_password
from app.database import Base, engine, get_db
from app import db_models
from app import user_models
from app.user_models import UserDB
from app.db_models import LeadDB, LeadNoteDB, LeadHistoryDB
from app.jwt import create_access_token, get_current_user


Base.metadata.create_all(bind=engine)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


security = HTTPBearer()


def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        token_user = get_current_user(token)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Nieprawidłowy token"
        )

    user = db.query(UserDB).filter(
        UserDB.id == token_user["id"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Konto użytkownika nie istnieje"
        )

    return {
        "id": user.id,
        "username": user.username,
        "role": user.role
    }


def require_role(*required_roles: str):
    def role_checker(
        current_user: dict = Depends(get_current_user_from_token)
    ):
        if current_user["role"] not in required_roles:
            raise HTTPException(
                status_code=403,
                detail="Brak uprawnień"
            )

        return current_user

    return role_checker


def get_accessible_lead(
    db: Session,
    lead_id: int,
    current_user: dict
):
    """
    Pobiera leada, jeśli użytkownik ma do niego dostęp.
    Administrator ma dostęp do wszystkich leadów.
    Pozostali użytkownicy widzą wyłącznie własne rekordy.
    """

    query = db.query(LeadDB).filter(LeadDB.id == lead_id)

    if current_user["role"] != "admin":
        query = query.filter(
            LeadDB.user_id == current_user["id"]
        )

    lead = query.first()

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead nie został znaleziony"
        )

    return lead
        

@app.get("/")
def home():
    return {"message": "SmartLead AI działa!"}


def add_history(db: Session, lead_id: int, action: str, details: str):
    db.add(
        LeadHistoryDB(
            lead_id=lead_id,
            action=action,
            details=details
        )
    )
    

@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(UserDB).filter(
        UserDB.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Użytkownik o tej nazwie już istnieje"
        )

    password_hash = hash_password(user.password)

    new_user = UserDB(
        username=user.username,
        password_hash=password_hash,
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Użytkownik został utworzony",
        "username": new_user.username
    }


@app.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    existing_user = db.query(UserDB).filter(
        UserDB.username == user.username
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Nieprawidłowa nazwa użytkownika lub hasło"
        )

    if not verify_password(user.password, existing_user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Nieprawidłowa nazwa użytkownika lub hasło"
        )

    access_token = create_access_token({
        "sub": existing_user.username,
        "role": existing_user.role,
        "user_id": existing_user.id
    })

    return {
        "message": "Logowanie zakończone pomyślnie",
        "username": existing_user.username,
        "access_token": access_token
    }

@app.post("/leads", response_model=LeadResponse)
def create_lead(
    lead: Lead,
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    analysis = analyze_lead(lead.message)

    lead_db = LeadDB(
        user_id=current_user["id"],
        name=lead.name,
        email=str(lead.email),
        message=lead.message,
        category=analysis.category,
        priority=analysis.priority,
        score=analysis.score,
        lead_level=analysis.lead_level,
        status="new"
    )

    db.add(lead_db)
    db.commit()
    db.refresh(lead_db)

    history = LeadHistoryDB(
        lead_id=lead_db.id,
        action="created",
        details="Lead został utworzony"
    )

    db.add(history)
    db.commit()

    return {
        "message": "Dane klienta zostały odebrane.",
        "lead": lead,
        "analysis": analysis
    }


@app.get("/leads", response_model=list[LeadDBResponse])
def get_leads(
    current_user: dict = Depends(get_current_user_from_token),
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

    if current_user["role"] != "admin":
        query = query.filter(
        LeadDB.user_id == current_user["id"]
    )

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


@app.get("/stats")
def get_stats(
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    # Pobranie leadów dostępnych dla zalogowanego użytkownika.
    query = db.query(LeadDB)

    # Administrator widzi wszystkie leady.
    # Pozostali użytkownicy widzą wyłącznie własne.
    if current_user["role"] != "admin":
        query = query.filter(
            LeadDB.user_id == current_user["id"]
        )

    # Łączna liczba leadów.
    total = query.count()

    # Liczba leadów według priorytetu.
    high_priority = query.filter(
        LeadDB.priority == "high"
    ).count()

    normal_priority = query.filter(
        LeadDB.priority == "normal"
    ).count()

    # Liczba leadów według statusu.
    statuses = {}

    for status in ["new", "contacted", "in_progress", "closed"]:
        statuses[status] = query.filter(
            LeadDB.status == status
        ).count()

    # Liczba leadów według kategorii.
    categories = {}

    category_names = (
        query.with_entities(LeadDB.category)
        .distinct()
        .all()
    )

    for category in category_names:
        category_name = category[0]

        categories[category_name] = query.filter(
            LeadDB.category == category_name
        ).count()

    return {
        "total": total,
        "high_priority": high_priority,
        "normal_priority": normal_priority,
        "statuses": statuses,
        "categories": categories
    }
    
    
@app.get("/leads/{lead_id}/history")
def get_lead_history(
    lead_id: int,
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    lead = get_accessible_lead(db, lead_id, current_user)

    history = (
        db.query(LeadHistoryDB)
        .filter(LeadHistoryDB.lead_id == lead.id)
        .order_by(LeadHistoryDB.created_at.asc())
        .all()
    )

    return {
        "lead_id": lead_id,
        "history": [
            {
                "id": item.id,
                "action": item.action,
                "details": item.details,
                "created_at": item.created_at
            }
            for item in history
        ]
    }


@app.get("/leads/{lead_id}", response_model=LeadDBResponse)
def get_lead(
    lead_id: int,
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    return get_accessible_lead(db, lead_id, current_user)


@app.get("/leads/{lead_id}/notes")
def get_lead_notes(
    lead_id: int,
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    lead = get_accessible_lead(db, lead_id, current_user)

    notes = (
        db.query(LeadNoteDB)
        .filter(LeadNoteDB.lead_id == lead.id)
        .order_by(LeadNoteDB.created_at.asc())
        .all()
    )

    return {
        "lead_id": lead_id,
        "notes": [
            {
                "id": note.id,
                "content": note.content,
                "created_at": note.created_at
            }
            for note in notes
        ]
    }


@app.post("/leads/{lead_id}/notes")
def create_lead_note(
    lead_id: int,
    note: LeadNoteCreate,
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    lead = get_accessible_lead(db, lead_id, current_user)

    new_note = LeadNoteDB(
        lead_id=lead.id,
        content=note.content
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return {
        "message": "Notatka została dodana",
        "note": {
            "id": new_note.id,
            "lead_id": new_note.lead_id,
            "content": new_note.content,
            "created_at": new_note.created_at
        }
    }


@app.delete("/leads/{lead_id}")
def delete_lead(
    lead_id: int,
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    lead = get_accessible_lead(db, lead_id, current_user)

    db.query(LeadNoteDB).filter(
        LeadNoteDB.lead_id == lead_id
    ).delete()

    db.query(LeadHistoryDB).filter(
        LeadHistoryDB.lead_id == lead_id
    ).delete()

    db.delete(lead)
    db.commit()

    return {"message": "Lead został usunięty"}


@app.put("/leads/{lead_id}")
def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    existing_lead = get_accessible_lead(
        db,
        lead_id,
        current_user
    )

    prepare_lead_update(lead_update, existing_lead)

    db.commit()
    db.refresh(existing_lead)

    return existing_lead


@app.patch("/leads/{lead_id}/status", response_model=LeadDBResponse)
def update_lead_status(
    lead_id: int,
    status_update: LeadStatusUpdate,
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    lead = get_accessible_lead(
        db,
        lead_id,
        current_user
    )

    old_status = lead.status
    lead.status = status_update.status

    if old_status != lead.status:
        add_history(
            db,
            lead_id,
            "status_changed",
            f"Status zmieniony: {old_status} → {lead.status}"
        )

    db.commit()
    db.refresh(lead)

    return lead