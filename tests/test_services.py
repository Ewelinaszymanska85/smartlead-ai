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