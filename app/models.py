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
    
    
class LeadDBResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    message: str
    category: str
    priority: Literal["normal", "high"]

    model_config = {
        "from_attributes": True
    }
    
    
class LeadUpdate(BaseModel):
    name: str
    email: EmailStr
    message: str
    
    
class LeadStats(BaseModel):
    total: int
    high_priority: int
    normal_priority: int
    categories: dict[str, int]