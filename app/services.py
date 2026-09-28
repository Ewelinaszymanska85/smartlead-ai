from app.models import LeadAnalysis


def analyze_lead(message: str):
    message = message.lower()

    if "sklep" in message:
        category = "sklep internetowy"
    elif "aplikacj" in message:
        category = "aplikacja mobilna"
    elif "stron" in message:
        category = "strona internetowa"
    else:
        category = "inne"

    score = 0

    if "pilnie" in message or "jak najszybciej" in message or "na już" in message:
        priority = "high"
        score += 30
    else:
        priority = "normal"

    if category == "sklep internetowy":
        score += 20
    elif category == "aplikacja mobilna":
        score += 15
    elif category == "strona internetowa":
        score += 10
        
    if len(message.split()) >= 8:
        score += 5

    if score >= 40:
        lead_level = "high"
    elif score >= 20:
        lead_level = "medium"
    else:
        lead_level = "low"

    return LeadAnalysis(
        category=category,
        priority=priority,
        score=score,
        lead_level=lead_level
    )


def prepare_lead_update(lead, existing_lead):
    analysis = analyze_lead(lead.message)

    existing_lead.name = lead.name
    existing_lead.email = str(lead.email)
    existing_lead.message = lead.message
    existing_lead.category = analysis.category
    existing_lead.priority = analysis.priority
    existing_lead.score = analysis.score
    existing_lead.lead_level = analysis.lead_level

    return existing_lead