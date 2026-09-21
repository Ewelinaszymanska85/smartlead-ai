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
        
    if "pilnie" in message or "jak najszybciej" in message or "na już" in message:
        priority = "high"
    else:
        priority = "normal"

    return LeadAnalysis(
        category=category,
        priority=priority
    ) 