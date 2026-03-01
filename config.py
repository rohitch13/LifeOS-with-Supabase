from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Base unauthenticated client (for login)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_authed_client(access_token: str):
    """Returns a Supabase client authenticated with the user's token."""
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    client.postgrest.auth(access_token)
    return client