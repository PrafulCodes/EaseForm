"""
Authentication dependencies for FastAPI.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.supabase import get_supabase_client
from supabase import Client

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase_client)
) -> dict:
    """
    Dependency to get current authenticated user from JWT token.
    
    Validates the Supabase JWT and returns user data.
    Raises 401 if token is invalid or expired.
    """
    token = credentials.credentials
    
    try:
        # Verify token with Supabase
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_response.user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_authenticated_client(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Client:
    """
    Get Supabase client with user's JWT token.
    This client will respect RLS policies for the authenticated user.
    """
    token = credentials.credentials
    
    from app.config import get_settings
    from supabase import create_client
    
    settings = get_settings()
    
    # Create client with user's access token
    # This ensures RLS policies use auth.uid() correctly
    client = create_client(settings.supabase_url, settings.supabase_anon_key)
    client.auth.set_session(token, token)  # Set the access token
    
    return client
