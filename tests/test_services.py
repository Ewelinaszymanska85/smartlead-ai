from app.services import analyze_lead
from app.jwt import create_access_token, get_current_user
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


def test_create_lead_endpoint(client, auth_headers):
    response = client.post(
        "/leads",
        headers=auth_headers,
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


def test_get_leads_endpoint(client, auth_headers):
    response = client.get(
        "/leads",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_get_leads_filters_by_priority(client, auth_headers):
    client.post(
        "/leads",
        json={
            "name": "Jan Kowalski",
            "email": "jan@example.com",
            "message": "Potrzebuję sklepu internetowego pilnie"
        }
    )

    response = client.get(
        "/leads?priority=high",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["priority"] == "high"


def test_get_leads_rejects_invalid_priority(client, auth_headers):
    response = client.get(
        "/leads?priority=xyz",
        headers=auth_headers
    )

    assert response.status_code == 422


def test_get_leads_filters_by_priority_and_category(client, auth_headers):
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
        "/leads?priority=high&category=sklep%20internetowy",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Jan Kowalski"
    assert data[0]["priority"] == "high"
    assert data[0]["category"] == "sklep internetowy"


def test_get_leads_supports_pagination(client, auth_headers):
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

    client.post(
        "/leads",
        json={
            "name": "Piotr Nowak",
            "email": "piotr@example.com",
            "message": "Potrzebuję aplikacji mobilnej"
        }
    )

    response = client.get(
        "/leads?limit=2&offset=0",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


def test_get_leads_rejects_invalid_limit(client, auth_headers):
    response = client.get(
        "/leads?limit=0",
        headers=auth_headers
    )

    assert response.status_code == 422


def test_get_leads_rejects_invalid_offset(client, auth_headers):
    response = client.get(
        "/leads?offset=-1",
        headers=auth_headers
    )

    assert response.status_code == 422


def test_get_lead_by_id(client, auth_headers):
    client.post(
        "/leads",
        json={
            "name": "Jan Kowalski",
            "email": "jan@example.com",
            "message": "Potrzebuję sklepu internetowego pilnie"
        }
    )

    response = client.get(
        "/leads/1",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Jan Kowalski"
    assert data["category"] == "sklep internetowy"
    assert data["priority"] == "high"


def test_get_lead_by_id_returns_404_for_missing_lead(
    client,
    auth_headers
):
    response = client.get(
        "/leads/999",
        headers=auth_headers
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Lead nie został znaleziony"


def test_delete_lead(client, auth_headers):
    client.post(
        "/leads",
        json={
            "name": "Piotr Testowy",
            "email": "piotr@example.com",
            "message": "Potrzebuję strony internetowej"
        }
    )

    response = client.delete(
        "/leads/1",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Lead został usunięty"

    get_response = client.get(
        "/leads/1",
        headers=auth_headers
    )

    assert get_response.status_code == 404


def test_delete_lead_returns_404_for_missing_lead(
    client,
    auth_headers
):
    response = client.delete(
        "/leads/999",
        headers=auth_headers
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Lead nie został znaleziony"


def test_update_lead(client, auth_headers):
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
        headers=auth_headers,
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


def test_update_lead_returns_404_for_missing_lead(
    client,
    auth_headers
):
    response = client.put(
        "/leads/999",
        headers=auth_headers,
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


def test_filter_leads_by_search(client, auth_headers):
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

    response = client.get(
        "/leads?search=sklep",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Anna"
    assert data[0]["category"] == "sklep internetowy"


def test_sort_leads_by_newest(client, auth_headers):
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

    response = client.get(
        "/leads?sort=newest",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Piotr"
    assert data[1]["name"] == "Anna"


def test_sort_leads_by_oldest(client, auth_headers):
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

    response = client.get(
        "/leads?sort=oldest",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Anna"
    assert data[1]["name"] == "Piotr"


def test_invalid_category(client, auth_headers):
    response = client.get(
        "/leads?category=nieistniejaca",
        headers=auth_headers
    )

    assert response.status_code == 422


def test_search_too_short(client, auth_headers):
    response = client.get(
        "/leads?search=a",
        headers=auth_headers
    )

    assert response.status_code == 422


def test_invalid_sort(client, auth_headers):
    response = client.get(
        "/leads?sort=invalid",
        headers=auth_headers
    )

    assert response.status_code == 422


def test_search_lead_by_name(client, auth_headers):
    client.post(
        "/leads",
        json={
            "name": "Anna Kowalska",
            "email": "anna@example.com",
            "message": "Potrzebuję strony internetowej"
        }
    )

    response = client.get(
        "/leads?search=Anna",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Anna Kowalska"


def test_search_lead_by_email(client, auth_headers):
    client.post(
        "/leads",
        json={
            "name": "Piotr Nowak",
            "email": "piotr@example.com",
            "message": "Chcę aplikację mobilną"
        }
    )

    response = client.get(
        "/leads?search=piotr@example.com",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["email"] == "piotr@example.com"


def test_search_lead_is_case_insensitive(client, auth_headers):
    client.post(
        "/leads",
        json={
            "name": "Anna Kowalska",
            "email": "anna@example.com",
            "message": "Potrzebuję strony internetowej"
        }
    )

    response = client.get(
        "/leads?search=ANNA",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Anna Kowalska"


def test_search_with_priority_filter(client, auth_headers):
    client.post(
        "/leads",
        json={
            "name": "Anna",
            "email": "anna@example.com",
            "message": "Potrzebuję sklepu internetowego pilnie"
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

    response = client.get(
        "/leads?search=sklep&priority=high",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Anna"
    assert data[0]["priority"] == "high"


def test_search_with_category_filter(client, auth_headers):
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

    response = client.get(
        "/leads?search=Potrzebuję&category=sklep%20internetowy",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Anna"
    assert data[0]["category"] == "sklep internetowy"


def test_filter_leads_by_created_from(client, auth_headers):
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

    response = client.get(
        "/leads?created_from=2026-09-24",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


def test_filter_leads_by_created_to(client, auth_headers):
    client.post(
        "/leads",
        json={
            "name": "Kasia",
            "email": "kasia@example.com",
            "message": "Potrzebuję aplikacji mobilnej"
        }
    )

    client.post(
        "/leads",
        json={
            "name": "Marek",
            "email": "marek@example.com",
            "message": "Potrzebuję strony internetowej"
        }
    )

    response = client.get(
        "/leads?created_to=2026-09-25",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


def test_filter_leads_by_created_date_range(client, auth_headers):
    client.post(
        "/leads",
        json={
            "name": "Ola",
            "email": "ola@example.com",
            "message": "Potrzebuję strony internetowej"
        }
    )

    client.post(
        "/leads",
        json={
            "name": "Tomek",
            "email": "tomek@example.com",
            "message": "Potrzebuję sklepu internetowego"
        }
    )

    response = client.get(
        "/leads?created_from=2026-09-24&created_to=2026-09-25",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


def test_invalid_created_from(client, auth_headers):
    response = client.get(
        "/leads?created_from=abc",
        headers=auth_headers
    )

    assert response.status_code == 422


def test_invalid_created_to(client, auth_headers):
    response = client.get(
        "/leads?created_to=abc",
        headers=auth_headers
    )

    assert response.status_code == 422


def test_invalid_created_date_range(client, auth_headers):
    response = client.get(
        "/leads?created_from=2026-09-25&created_to=2026-09-24",
        headers=auth_headers
    )

    assert response.status_code == 422


def test_update_lead_status(client, auth_headers):
    client.post(
        "/leads",
        json={
            "name": "Anna",
            "email": "anna@example.com",
            "message": "Potrzebuję strony internetowej"
        }
    )

    response = client.get(
        "/leads",
        headers=auth_headers
    )

    assert response.status_code == 200

    leads = response.json()
    lead_id = leads[-1]["id"]

    response = client.patch(
        f"/leads/{lead_id}/status",
        json={
            "status": "contacted"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "contacted"


def test_invalid_lead_status(client, auth_headers):
    response = client.post(
        "/leads",
        json={
            "name": "Anna",
            "email": "anna@example.com",
            "message": "Potrzebuję strony internetowej"
        }
    )

    response = client.get(
        "/leads",
        headers=auth_headers
    )

    assert response.status_code == 200

    leads = response.json()
    lead_id = leads[-1]["id"]

    response = client.patch(
        f"/leads/{lead_id}/status",
        json={
            "status": "xyz"
        }
    )

    assert response.status_code == 422


def test_update_status_for_missing_lead(client):
    response = client.patch(
        "/leads/9999/status",
        json={
            "status": "contacted"
        }
    )

    assert response.status_code == 404


def test_register_user(client):
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "password": "Test123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "testuser"
    assert data["message"] == "Użytkownik został utworzony"


def test_login_user(client):
    client.post(
        "/register",
        json={
            "username": "loginuser",
            "password": "Test123"
        }
    )

    response = client.post(
        "/login",
        json={
            "username": "loginuser",
            "password": "Test123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "loginuser"
    assert data["message"] == "Logowanie zakończone pomyślnie"
    assert "access_token" in data
    assert isinstance(data["access_token"], str)


def test_login_with_wrong_password(client):
    client.post(
        "/register",
        json={
            "username": "wrongpassworduser",
            "password": "Test123"
        }
    )

    response = client.post(
        "/login",
        json={
            "username": "wrongpassworduser",
            "password": "ZleHaslo"
        }
    )

    assert response.status_code == 401


def test_login_with_unknown_user(client):
    response = client.post(
        "/login",
        json={
            "username": "nieistniejacy",
            "password": "Test123"
        }
    )

    assert response.status_code == 401


def test_create_access_token():
    token = create_access_token({"sub": "admin"})

    assert token is not None
    assert isinstance(token, str)


def test_get_current_user():
    token = create_access_token({"sub": "admin"})

    username = get_current_user(token)

    assert username == "admin"