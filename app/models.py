from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class Lead(BaseModel):
    name: str
    email: EmailStr
    message: str


class LeadAnalysis(BaseModel):
    category: str
    priority: Literal["normal", "high"]
    score: int
    lead_level: Literal["low", "medium", "high"]

class LeadResponse(BaseModel):
    message: str
    lead: Lead
    analysis: LeadAnalysis
    
    
class LeadDBResponse(BaseModel):
    id: int
    created_at: datetime
    name: str
    email: EmailStr
    message: str
    category: str
    priority: Literal["normal", "high"]
    score: int
    lead_level: Literal["low", "medium", "high"]
    status: Literal["new", "contacted", "in_progress", "closed"]

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
    
    
class LeadStatusUpdate(BaseModel):
    status: Literal["new", "contacted", "in_progress", "closed"]
    
    
class UserCreate(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=8)
    
    
class UserLogin(BaseModel):
    username: str
    password: str