"""
Forms API router.
Handles CRUD operations for forms.
# Trigger reload 4
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from uuid import UUID
from supabase import Client
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.form import FormCreate, FormUpdate, FormResponse, FormListItem
from app.dependencies import get_current_user, get_authenticated_client
from app.utils.supabase import get_supabase_client, get_supabase_admin
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/forms", tags=["forms"])


@router.post("", response_model=FormResponse, status_code=status.HTTP_201_CREATED)
@Limiter(key_func=get_remote_address).limit("10/minute")
async def create_form(
    request: Request,
    form_data: FormCreate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_client)
):
    """
    Create a new form.
    
    Requires authentication. Form will be owned by the authenticated user.
    """
    try:
        user_id = current_user.id
        logger.info(f"Authenticated user: {user_id}")
        logger.info(f"Creating form with host_id: {user_id}")

        # Prepare form data with flat structure matching DB columns
        form_dict = {
            "host_id": current_user.id,
            "title": form_data.title,
            "description": form_data.description,
            "questions": [q.model_dump() for q in form_data.questions],
            "is_active": form_data.is_active,
            # Flat boolean fields (no nested settings)
            # FORCE PRIVACY SETTINGS
            "anonymous": True,
            "one_response_per_device": True,
            # Ignore closed on create, default to False
            "closed": False 
        }
        
        # Ensure host exists in hosts table (Using Admin Client to bypass RLS)
        try:
            # We must use admin client because if the host record doesn't exist,
            # the user might not have permission to 'select' it (returning empty)
            # or 'insert' it depending on strict RLS policies.
            # Admin client ensures we can check and create without permission issues.
            admin_client = get_supabase_admin()
            
            # Check if host exists
            host_response = admin_client.table("hosts").select("id").eq("id", current_user.id).execute()
            
            if not host_response.data:
                logger.info(f"Host profile missing for {current_user.id}, creating one via Admin...")
                # Create host profile
                email = current_user.email if hasattr(current_user, 'email') else f"{current_user.id}@placeholder.com"
                name = email.split("@")[0]
                
                admin_client.table("hosts").insert({
                    "id": current_user.id,
                    "email": email,
                    "name": name,
                    "active_forms_count": 0
                }).execute()
        except Exception as e:
            logger.error(f"Error checking/creating host profile: {e}")
            # We should probably fail here if we couldn't ensure the host exists,
            # otherwise the FK violation occurs.
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize host profile: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error checking/creating host profile: {e}")
            # Continue anyway, let the FK constraint fail if it must
        
        # Insert into database (RLS will enforce host_id = auth.uid())
        response = supabase.table("forms").insert(form_dict).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create form"
            )
        
        return response.data[0]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating form: {str(e)}"
        )


@router.get("", response_model=List[FormListItem])
@Limiter(key_func=get_remote_address).limit("30/minute")
async def list_forms(
    request: Request,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_client)
):
    """
    List all forms owned by the authenticated user.
    
    Returns simplified form data for list views.
    Now includes distinct statuses and response counts.
    """
    try:
        user_id = current_user.id
        logger.info(f"List forms requested by user {user_id}")

        # Query forms (RLS ensures only user's forms are returned)
        # We include 'closed' and 'is_active' for status determination
        response = supabase.table("forms")\
            .select("id, title, description, is_active, closed, created_at")\
            .eq("host_id", user_id)\
            .order("created_at", desc=True)\
            .execute()
        
        forms = response.data
        
        
        # Ensure "closed" is present (it might be null in DB if old row)
        for form in forms:
            if "closed" not in form or form["closed"] is None:
                form["closed"] = False

        logger.info(f"Found {len(forms)} forms for user {user_id}")
        
        if forms:
            logger.info(f"Returning {len(forms)} forms. Sample 1: {forms[0].get('title')} - Closed: {forms[0].get('closed')}")
        else:
            logger.info(f"No forms found for user {user_id}")
        
        return forms
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching forms: {str(e)}"
        )



@router.get("/{form_id}", response_model=FormResponse)
@Limiter(key_func=get_remote_address).limit("60/minute")
async def get_form(
    request: Request,
    form_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_client)
):
    """
    Get a specific form by ID.
    
    Requires authentication. Only the form owner can access.
    """
    try:
        user_id = current_user.id
        
        # Query form (RLS ensures only owner can access)
        response = supabase.table("forms")\
            .select("*")\
            .eq("id", str(form_id))\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found or permission denied"
            )
            
        form = response.data[0]
        
        
        # Ensure "closed" is present
        if "closed" not in form or form["closed"] is None:
            form["closed"] = False
            
        return form
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching form: {str(e)}"
        )


@router.put("/{form_id}", response_model=FormResponse)
@Limiter(key_func=get_remote_address).limit("30/minute")
async def update_form(
    request: Request,
    form_id: UUID,
    form_data: FormUpdate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_client)
):
    """
    Update an existing form.
    
    Requires authentication. Only the form owner can update.
    Enforces privacy settings (anonymous=True, one_response_per_device=True).
    Does NOT update 'closed' status (use PATCH /stop for that).
    """
    try:
        user_id = current_user.id
        logger.info(f"Updating form {form_id} for user {user_id}")
        
        # Prepare update data
        update_dict = {
            "title": form_data.title,
            "questions": [q.model_dump() for q in form_data.questions] if form_data.questions is not None else None,
            "updated_at": "now()", # Let DB handle if default, but explicit is good
            # FORCE PRIVACY SETTINGS
            "anonymous": True,
            "one_response_per_device": True
        }
        
        # Add optional fields only if provided
        if form_data.description is not None:
            update_dict["description"] = form_data.description
            
        if form_data.is_active is not None:
            update_dict["is_active"] = form_data.is_active

        # Filter out None values to avoid overwriting with null
        update_payload = {k: v for k, v in update_dict.items() if v is not None}
        
        # Perform update (RLS ensures ownership)
        response = supabase.table("forms")\
            .update(update_payload)\
            .eq("id", str(form_id))\
            .execute()
            
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found or permission denied"
            )
            
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating form: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating form: {str(e)}"
        )


@router.patch("/{form_id}/stop", response_model=FormResponse)
@Limiter(key_func=get_remote_address).limit("10/minute")
async def stop_form(
    request: Request,
    form_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_client)
):
    """
    Stop receiving responses for a form.
    
    Sets closed=True and is_active=False.
    This action is strictly one-way for now.
    """
    try:
        user_id = current_user.id
        logger.info(f"Stopping form {form_id} for user {user_id}")
        
        # 1. Try standard update (RLS)
        response = supabase.table("forms")\
            .update({
                "closed": True,
                "is_active": False
            })\
            .eq("id", str(form_id))\
            .execute()
        
        if response.data:
            return response.data[0]

        # 2. If failed, it might be RLS blocking UPDATE.
        # Let's verify ownership via Admin and perform update if owned.
        logger.warning(f"Standard update failed for form {form_id}. Checking ownership via Admin...")
        
        admin_client = get_supabase_admin()
        
        # Check ownership
        form_check = admin_client.table("forms")\
            .select("host_id")\
            .eq("id", str(form_id))\
            .maybe_single()\
            .execute()
            
        if not form_check.data:
            logger.error(f"Form {form_id} not found/active")
            raise HTTPException(status_code=404, detail="Form not found")
            
        real_host_id = form_check.data.get("host_id")
        
        if real_host_id != user_id:
            logger.error(f"Permission denied. Owner: {real_host_id}, Requester: {user_id}")
            raise HTTPException(status_code=404, detail="Form not found or permission denied")
            
        # Ownership verified. Perform update via Admin (Bypassing RLS)
        logger.info(f"Ownership verified. Force stopping form {form_id} via Admin.")
        
        admin_update = admin_client.table("forms")\
            .update({
                "closed": True,
                "is_active": False
            })\
            .eq("id", str(form_id))\
            .execute()
            
        return admin_update.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping form: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error stopping form: {str(e)}"
        )


@router.delete("/{form_id}")
@Limiter(key_func=get_remote_address).limit("10/minute")
async def delete_form(
    request: Request,
    form_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_client)
):
    """
    Delete a form.
    
    Requires authentication. Only the form owner can delete.
    This will cascade delete all responses.
    """
    try:
        # Delete form (RLS ensures only owner can delete)
        response = supabase.table("forms")\
            .delete()\
            .eq("id", str(form_id))\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found or you don't have permission to delete it"
            )
        
        return {"message": "Form deleted successfully", "id": str(form_id)}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting form: {str(e)}"
        )
