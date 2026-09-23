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
    
    
def test_get_leads_supports_pagination(client):
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

    response = client.get("/leads?limit=1&offset=1")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Anna Nowak"
    
    
def test_get_leads_rejects_invalid_limit(client):
    response = client.get("/leads?limit=0")

    assert response.status_code == 422


def test_get_leads_rejects_invalid_offset(client):
    response = client.get("/leads?offset=-1")

    assert response.status_code == 422
    
    
def test_get_lead_by_id(client):
    client.post(
        "/leads",
        json={
            "name": "Jan Kowalski",
            "email": "jan@example.com",
            "message": "Potrzebuję sklepu internetowego pilnie"
        }
    )

    response = client.get("/leads/1")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Jan Kowalski"
    assert data["category"] == "sklep internetowy"
    assert data["priority"] == "high"
    
    
def test_get_lead_by_id_returns_404_for_missing_lead(client):
    response = client.get("/leads/999")

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Lead nie został znaleziony"
    
    
def test_delete_lead(client):
    client.post(
        "/leads",
        json={
            "name": "Piotr Testowy",
            "email": "piotr@example.com",
            "message": "Potrzebuję strony internetowej"
        }
    )

    response = client.delete("/leads/1")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Lead został usunięty"

    get_response = client.get("/leads/1")

    assert get_response.status_code == 404
    
    
def test_delete_lead_returns_404_for_missing_lead(client):
    response = client.delete("/leads/999")

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Lead nie został znaleziony"
    
    
def test_update_lead(client):
    client.post(
        "/leads",
        json={
            "name": "Anna Testowa",
            "email": "anna@example.com",
            "message": "Potrzebuję strony internetowej"
        }
    )

    response = client.put(
        "/leads/1",
        json={
            "name": "Anna Kowalska",
            "email": "anna@example.com",
            "message": "Potrzebuję sklepu internetowego pilnie"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Anna Kowalska"
    assert data["email"] == "anna@example.com"
    assert data["message"] == "Potrzebuję sklepu internetowego pilnie"
    assert data["category"] == "sklep internetowy"
    assert data["priority"] == "high"
    
    
def test_update_lead_returns_404_for_missing_lead(client):
    response = client.put(
        "/leads/999",
        json={
            "name": "Anna Kowalska",
            "email": "anna@example.com",
            "message": "Potrzebuję sklepu internetowego"
        }
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Lead nie został znaleziony"
    
    
def test_get_stats(client):
    client.post(
        "/leads",
        json={
            "name": "Anna Testowa",
            "email": "anna@example.com",
            "message": "Potrzebuję sklepu internetowego pilnie"
        }
    )

    client.post(
        "/leads",
        json={
            "name": "Piotr Testowy",
            "email": "piotr@example.com",
            "message": "Potrzebuję strony internetowej"
        }
    )

    response = client.get("/stats")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert data["high_priority"] == 1
    assert data["normal_priority"] == 1
    assert data["categories"]["sklep internetowy"] == 1
    assert data["categories"]["strona internetowa"] == 1
    
    
def test_filter_leads_by_search(client):
    client.post(
        "/leads",
        json={
            "name": "Anna",
            "email": "anna@example.com",
            "message": "Potrzebuję sklepu internetowego"
        }
    )

    client.post(
        "/leads",
        json={
            "name": "Piotr",
            "email": "piotr@example.com",
            "message": "Potrzebuję strony internetowej"
        }
    )

    response = client.get("/leads?search=sklep")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Anna"
    assert data[0]["category"] == "sklep internetowy"
    
    
def test_sort_leads_by_newest(client):
    client.post(
        "/leads",
        json={
            "name": "Anna",
            "email": "anna@example.com",
            "message": "Potrzebuję strony internetowej"
        }
    )

    client.post(
        "/leads",
        json={
            "name": "Piotr",
            "email": "piotr@example.com",
            "message": "Potrzebuję sklepu internetowego"
        }
    )

    response = client.get("/leads?sort=newest")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Piotr"
    assert data[1]["name"] == "Anna"
    
    
def test_sort_leads_by_oldest(client):
    client.post(
        "/leads",
        json={
            "name": "Anna",
            "email": "anna@example.com",
            "message": "Potrzebuję strony internetowej"
        }
    )

    client.post(
        "/leads",
        json={
            "name": "Piotr",
            "email": "piotr@example.com",
            "message": "Potrzebuję sklepu internetowego"
        }
    )

    response = client.get("/leads?sort=oldest")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Anna"
    assert data[1]["name"] == "Piotr"
    
    
def test_invalid_category(client):
    response = client.get("/leads?category=nieistniejaca")

    assert response.status_code == 422
    
    
def test_search_too_short(client):
    response = client.get("/leads?search=a")

    assert response.status_code == 422
    
    
def test_invalid_sort(client):
    response = client.get("/leads?sort=invalid")

    assert response.status_code == 422
    
    
def test_search_lead_by_name(client):
    client.post(
        "/leads",
        json={
            "name": "Anna Kowalska",
            "email": "anna@example.com",
            "message": "Potrzebuję strony internetowej"
        }
    )

    response = client.get("/leads?search=Anna")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Anna Kowalska"
    
    
def test_search_lead_by_email(client):
    client.post(
        "/leads",
        json={
            "name": "Piotr Nowak",
            "email": "piotr@example.com",
            "message": "Chcę aplikację mobilną"
        }
    )

    response = client.get("/leads?search=piotr@example.com")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["email"] == "piotr@example.com"