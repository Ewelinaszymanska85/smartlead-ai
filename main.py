from fastapi import FastAPI
from app.models import Lead, LeadResponse
from app.services import analyze_lead

app = FastAPI()


@app.get("/")
def home():
    return {"message": "SmartLead AI działa!"}


@app.post("/leads", response_model=LeadResponse)
def create_lead(lead: Lead):
    analysis = analyze_lead(lead.message)

    return {
        "message": "Dane klienta zostały odebrane.",
        "lead": lead,
        "analysis": analysis
    }