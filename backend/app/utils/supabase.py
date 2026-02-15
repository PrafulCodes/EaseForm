"""
Supabase client utilities.
"""

from supabase import create_client, Client
from app.config import get_settings

settings = get_settings()


import logging

logger = logging.getLogger(__name__)

def get_supabase_client() -> Client:
    """
    Get Supabase client with SERVICE ROLE key.
    
    WARNING: This client has full admin privileges and bypasses RLS.
    We are using this in the backend to ensure we can perform all necessary operations.
    RLS/Auth checks are handled at the application logic layer where needed,
    or by explicit RLS policies if we were using the anon key.
    
    However, for this application's design, we are switching to Service Role
    to avoid RLS friction for public operations while maintaining control.
    """
    key_type = "SERVICE ROLE"
    key = settings.supabase_service_key
    
    logger.info(f"Supabase Client initialized with {key_type} key")
    
    return create_client(
        settings.supabase_url,
        key
    )

def get_supabase_admin() -> Client:
    """
    Alias for get_supabase_client since we are now using service role by default.
    Kept for backward compatibility.
    """
    return get_supabase_client()

