from typing import Literal

from pydantic import BaseModel, EmailStr


class Lead(BaseModel):
    name: str
    email: EmailStr
    message: str


class LeadAnalysis(BaseModel):
    category: str
    priority: Literal["normal", "high"]


class LeadResponse(BaseModel):
    message: str
    lead: Lead
    analysis: LeadAnalysis