from app.services import analyze_lead
from pydantic import ValidationError
from app.models import LeadAnalysis


def test_analyze_lead_detects_category_and_high_priority():
    result = analyze_lead("Potrzebuję sklepu internetowego pilnie")

    assert result.category == "sklep internetowy"
    assert result.priority == "high"


def test_analyze_lead_detects_normal_priority():
    result = analyze_lead("Potrzebuję strony internetowej")

    assert result.category == "strona internetowa"
    assert result.priority == "normal"


def test_lead_analysis_rejects_invalid_priority():
    try:
        LeadAnalysis(
            category="inne",
            priority="bardzo pilne"
        )
        assert False
    except ValidationError:
        assert True
        

def test_create_lead_endpoint(client):
    response = client.post(
        "/leads",
        json={
            "name": "Anna Nowak",
            "email": "anna@example.com",
            "message": "Potrzebuję strony internetowej"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["lead"]["name"] == "Anna Nowak"
    assert data["analysis"]["category"] == "strona internetowa"
    assert data["analysis"]["priority"] == "normal"
    
    
def test_get_leads_endpoint(client):
    response = client.get("/leads")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list) 
    
    
def test_get_leads_filters_by_priority(client):
    client.post(
        "/leads",
        json={
            "name": "Jan Kowalski",
            "email": "jan@example.com",
            "message": "Potrzebuję sklepu internetowego pilnie"
        }
    )

    response = client.get("/leads?priority=high")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["priority"] == "high"
    
    
def test_get_leads_rejects_invalid_priority(client):
    response = client.get("/leads?priority=xyz")

    assert response.status_code == 422
    
    
def test_get_leads_filters_by_priority_and_category(client):
    client.post(
        "/leads",
        json={
            "name": "Jan Kowalski",
            "email": "jan@example.com",
            "message": "Potrzebuję sklepu internetowego pilnie"
        }
    )

    client.post(
        "/leads",
        json={
            "name": "Anna Nowak",
            "email": "anna@example.com",
            "message": "Potrzebuję strony internetowej"
        }
    )

    response = client.get(
        "/leads?priority=high&category=sklep%20internetowy"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Jan Kowalski"
    assert data[0]["priority"] == "high"
    assert data[0]["category"] == "sklep internetowy"