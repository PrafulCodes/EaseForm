"""
Responses API router.
Handles response submission and retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from uuid import UUID
from supabase import Client
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.response import ResponseSubmit, ResponseData
from app.dependencies import get_current_user, get_authenticated_client
from app.utils.supabase import get_supabase_client
from app.utils.security import generate_device_hash

router = APIRouter(tags=["responses"])


@router.post("/forms/{form_id}/responses", status_code=status.HTTP_201_CREATED)
@Limiter(key_func=get_remote_address).limit("10/minute")
async def submit_response(
    form_id: UUID,
    response_data: ResponseSubmit,
    request: Request,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Submit a response to a form.
    
    Public endpoint - no authentication required.
    Enforces one-response-per-device using device fingerprinting.
    """
    try:
        # Check if form exists and is active/open
        form_response = supabase.table("forms")\
            .select("id, is_active, closed")\
            .eq("id", str(form_id))\
            .single()\
            .execute()
        
        if not form_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found"
            )
        
        # Check if form is closed or inactive
        is_closed = form_response.data.get("closed", False)
        is_active = form_response.data.get("is_active", True)
        
        if is_closed or not is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This form is no longer accepting responses"
            )
        
        # Generate device hash
        device_hash = generate_device_hash(request, str(form_id))
        
        # Check if device already submitted
        existing_response = supabase.table("responses")\
            .select("id")\
            .eq("form_id", str(form_id))\
            .eq("device_hash", device_hash)\
            .execute()
        
        if existing_response.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already submitted a response to this form"
            )
        
        # Insert response
        response_dict = {
            "form_id": str(form_id),
            "answers": response_data.answers,
            "device_hash": device_hash
        }
        
        insert_response = supabase.table("responses")\
            .insert(response_dict)\
            .execute()
        
        if not insert_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit response"
            )
        
        return {
            "message": "Response submitted successfully",
            "response_id": insert_response.data[0]["id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting response: {str(e)}"
        )


@router.get("/forms/{form_id}/responses", response_model=List[ResponseData])
@Limiter(key_func=get_remote_address).limit("30/minute")
async def get_form_responses(
    request: Request,
    form_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_client)
):
    """
    Get all responses for a form.
    
    Requires authentication. Only the form owner can view responses.
    RLS policy enforces ownership check.
    """
    try:
        # Verify form ownership (RLS will also enforce this)
        form_response = supabase.table("forms")\
            .select("id, host_id")\
            .eq("id", str(form_id))\
            .single()\
            .execute()
        
        if not form_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found"
            )
        
        if form_response.data["host_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view these responses"
            )
        
        # Get responses (RLS ensures only owner can read)
        responses = supabase.table("responses")\
            .select("*")\
            .eq("form_id", str(form_id))\
            .order("created_at", desc=True)\
            .execute()
        
        # Normalize data to ensure strict shape
        # This prevents accidental wrapping or extra fields
        normalized = []
        for r in responses.data:
            # handle potential double-wrapping or missing fields safety
            answers = r.get("answers", {})
            
            # If answers is somehow null, make it empty dict
            if answers is None:
                answers = {}
                
            normalized.append({
                "id": r.get("id"),
                "form_id": r.get("form_id"), # Include form_id as it is part of ResponseData model
                "answers": answers,
                "device_hash": r.get("device_hash"),
                "created_at": r.get("created_at")
            })
            
        return normalized
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching responses: {str(e)}"
        )


@router.delete("/responses/{response_id}", status_code=status.HTTP_204_NO_CONTENT)
@Limiter(key_func=get_remote_address).limit("30/minute")
async def delete_response(
    request: Request,
    response_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_client)
):
    """
    Delete a specific response.
    
    Requires authentication. Only the form owner can delete responses.
    """
    try:
        # Delete response (RLS ensures only form owner can delete)
        delete_response = supabase.table("responses")\
            .delete()\
            .eq("id", str(response_id))\
            .execute()
        
        if not delete_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Response not found or you don't have permission to delete it"
            )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting response: {str(e)}"
        )
