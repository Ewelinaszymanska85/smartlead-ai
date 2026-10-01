# SmartLead AI

SmartLead AI to aplikacja REST API zbudowana w Pythonie i FastAPI.

Aplikacja służy do obsługi leadów sprzedażowych. Pozwala między innymi na:
- rejestrację i logowanie użytkowników,
- uwierzytelnianie za pomocą JWT,
- obsługę ról użytkowników,
- tworzenie, pobieranie, aktualizowanie i usuwanie leadów,
- automatyczną analizę leadów,
- określanie kategorii i priorytetu,
- wyliczanie score i poziomu leada,
- dodawanie notatek do leadów,
- zapisywanie historii działań na leadach,
- prezentowanie statystyk.

## Technologie

- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite
- JWT
- pytest
- Docker
- Docker Compose

## Uruchomienie lokalne

Aktywuj środowisko wirtualne:

```powershell
.\venv\Scripts\Activate.ps1