import streamlit as st
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def _headers(access_token: str):
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

def get_misc(access_token: str, user_id: str, key: str):
    """Fetch a single misc entry by key. Returns the data dict or {}."""
    try:
        res = requests.get(
            f"{SUPABASE_URL}/rest/v1/user_misc",
            headers=_headers(access_token),
            params={"user_id": f"eq.{user_id}", "key": f"eq.{key}", "select": "data"}
        )
        res.raise_for_status()
        rows = res.json()
        return rows[0]["data"] if rows else {}
    except Exception as e:
        st.error(f"Failed to load {key}: {e}")
        return {}

def set_misc(access_token: str, user_id: str, key: str, data: dict):
    """Upsert a misc entry. Creates or updates the row for this user+key."""
    try:
        res = requests.post(
            f"{SUPABASE_URL}/rest/v1/user_misc",
            headers={**_headers(access_token), "Prefer": "resolution=merge-duplicates,return=representation"},
            json={
                "user_id": user_id,
                "key": key,
                "data": data,
                "updated_at": "now()",
            }
        )
        res.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Failed to save {key}: {e}")
        return False