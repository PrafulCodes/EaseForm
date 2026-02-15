"""
Pydantic models for forms.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class QuestionOption(BaseModel):
    """Option for multiple choice, checkboxes, or dropdown questions."""
    value: str
    label: str


class Question(BaseModel):
    """Individual form question."""
    id: str
    question: str
    type: str  # short_answer, paragraph, multiple_choice, checkboxes, dropdown, linear_scale, date, time
    required: bool = False
    options: Optional[List[str]] = None  # For choice-based questions
    

class FormCreate(BaseModel):
    """Schema for creating a new form."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    questions: List[Question] = Field(default_factory=list)
    is_active: bool = True
    # Flat boolean fields instead of nested settings
    anonymous: bool = False
    one_response_per_device: bool = False
    closed: bool = False


class FormUpdate(BaseModel):
    """Schema for updating an existing form."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    questions: Optional[List[Question]] = None
    is_active: Optional[bool] = None
    # Flat boolean fields instead of nested settings
    anonymous: Optional[bool] = None
    one_response_per_device: Optional[bool] = None
    closed: Optional[bool] = None


class FormResponse(BaseModel):
    """Schema for form data returned to client."""
    id: UUID
    host_id: UUID
    title: str
    description: Optional[str]
    questions: List[Question]
    is_active: bool
    # Flat boolean fields instead of nested settings
    anonymous: bool
    one_response_per_device: bool
    closed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FormListItem(BaseModel):
    """Simplified form data for list views."""
    id: UUID
    title: str
    description: Optional[str]
    is_active: bool
    closed: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True
