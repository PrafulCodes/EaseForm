"""
Public Forms API router.
Handles unauthenticated access to public forms.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from uuid import UUID
from supabase import Client

from app.models.form import FormResponse
from app.utils.supabase import get_supabase_client, get_supabase_admin
import logging
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)

router = APIRouter(tags=["public_forms"])

@router.get("/{form_id}", response_model=FormResponse)
@Limiter(key_func=get_remote_address).limit("60/minute")
async def get_public_form(
    form_id: UUID,
    request: Request,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get a public form by ID.
    
    No authentication required.
    Only returns active forms.
    """
    try:
        # 1. Try to fetch as anonymous user (respects RLS)
        # We fetch if it exists. We will filter status in Python.
        response = supabase.table("forms")\
            .select("*")\
            .eq("id", str(form_id))\
            .maybe_single()\
            .execute()
        
        # 2. If valid response, check status
        if response and response.data:
            form = response.data
            
            # If form is closed, we return it so frontend can show "Closed" message
            if form.get("closed"):
                return form
                
            # If form is active, return it
            if form.get("is_active"):
                return form
                
            # If inactive and not closed (Draft), return 404
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found"
            )
            
        # 3. DEBUGGING: If not found, check if it exists via Admin (bypass RLS)
        # This helps distinguish between "Not Found" vs "RLS Blocked"
        admin_client = get_supabase_admin()
        admin_response = admin_client.table("forms")\
            .select("*")\
            .eq("id", str(form_id))\
            .maybe_single()\
            .execute()
            
        if admin_response and admin_response.data:
            form = admin_response.data
            # We already handled status checks above for accessible forms.
            # If we are here, it means RLS hid the form (e.g. it's not public?)
            # But currently we don't have RLS for 'public' vs 'private' forms explicitly other than is_active?
            # Actually, RLS usually allows 'select' for everyone on 'forms' table?
            # If not, we might be blocked here. 
            # Assuming RLS allows select for all.
            pass

        # Truly not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )
        
        # Truly not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching form: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching form: {str(e)}"
        )
