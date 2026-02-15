"""
Pydantic models for responses.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID


class ResponseSubmit(BaseModel):
    """Schema for submitting a form response."""
    answers: Dict[str, Any] = Field(
        ...,
        description="Question ID to answer mapping"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "answers": {
                    "question_1": "John Doe",
                    "question_2": "john@example.com",
                    "question_3": ["Option 1", "Option 3"]
                }
            }
        }


class ResponseData(BaseModel):
    """Schema for response data returned to form owner."""
    id: UUID
    form_id: UUID
    answers: Dict[str, Any]
    device_hash: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResponseSummary(BaseModel):
    """Summary statistics for a form's responses."""
    total_responses: int
    latest_response: Optional[datetime]
    question_stats: Optional[Dict[str, Any]] = None
