import os
from supabase import create_client, Client
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# read from environment (set these in Render Environment/ local .env kung mag local dev)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Anon client (read operations / public-safe calls)
supabase_anon = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Service client (server-side privileged calls). Keep service key secret.
supabase_service = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
supabase = supabase_service