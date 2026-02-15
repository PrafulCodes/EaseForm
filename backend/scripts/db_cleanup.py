import os
import sys
import asyncio
from supabase import create_client, Client

# Add backend directory to path to import config
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.config import get_settings

async def main():
    print("🧹 Starting Database Cleanup...")
    
    settings = get_settings()
    
    # Use service key to bypass RLS
    if not settings.supabase_service_key:
        print("❌ Error: SUPABASE_SERVICE_KEY not found in environment variables.")
        return

    supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)

    # 1. Remove orphaned forms
    print("\n🔍 Phase 1: Removing orphaned forms...")
    
    # Get all hosts IDs
    hosts_response = supabase.table("hosts").select("id").execute()
    host_ids = [h['id'] for h in hosts_response.data]
    print(f"   Found {len(host_ids)} valid hosts.")

    # Get all forms
    forms_response = supabase.table("forms").select("id, host_id").execute()
    forms = forms_response.data
    
    orphaned_forms = [f['id'] for f in forms if f['host_id'] not in host_ids]
    
    if orphaned_forms:
        print(f"   🗑️ Found {len(orphaned_forms)} orphaned forms. Deleting...")
        for form_id in orphaned_forms:
             supabase.table("forms").delete().eq("id", form_id).execute()
        print("   ✅ Orphaned forms deleted.")
    else:
        print("   ✅ No orphaned forms found.")


    # 2. Remove orphaned responses
    print("\n🔍 Phase 2: Removing orphaned responses...")
    
    # Get all valid form IDs (refresh list)
    forms_response = supabase.table("forms").select("id").execute()
    valid_form_ids = [f['id'] for f in forms_response.data]
    
    # Get all responses
    responses_response = supabase.table("responses").select("id, form_id").execute()
    responses = responses_response.data
    
    orphaned_responses = [r['id'] for r in responses if r['form_id'] not in valid_form_ids]
    
    if orphaned_responses:
         print(f"   🗑️ Found {len(orphaned_responses)} orphaned responses. Deleting...")
         for response_id in orphaned_responses:
             supabase.table("responses").delete().eq("id", response_id).execute()
         print("   ✅ Orphaned responses deleted.")
    else:
        print("   ✅ No orphaned responses found.")

    print("\n🔒 Phase 3: SQL Constraints (Manual Step)")
    print("   Since we cannot execute ALTER TABLE via the API, please run the following SQL in your Supabase SQL Editor:")
    print("-" * 50)
    print("""
ALTER TABLE forms
DROP CONSTRAINT IF EXISTS forms_host_id_fkey;

ALTER TABLE forms
ADD CONSTRAINT forms_host_id_fkey
FOREIGN KEY (host_id)
REFERENCES hosts(id)
ON DELETE CASCADE;
    """)
    print("-" * 50)

    print("\n✅ Cleanup process completed.")

if __name__ == "__main__":
    asyncio.run(main())
