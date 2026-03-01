import streamlit as st
import os
import requests
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

def get_expenses(access_token: str, user_id: str):
    try:
        res = requests.get(
            f"{SUPABASE_URL}/rest/v1/expenses",
            headers=_headers(access_token),
            params={"user_id": f"eq.{user_id}", "order": "date.desc", "select": "*"}
        )
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"Failed to fetch expenses: {e}")
        return []

def add_expense(access_token: str, user_id: str, date_val, amount: float, category: str, note: str, recurring: bool, tags: list):
    try:
        res = requests.post(
            f"{SUPABASE_URL}/rest/v1/expenses",
            headers=_headers(access_token),
            json={
                "user_id": user_id,
                "date": str(date_val),
                "amount": amount,
                "category": category,
                "note": note,
                "recurring": recurring,
                "tags": tags,
            }
        )
        res.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Failed to add expense: {e} — {res.text}")
        return False

def delete_expense(access_token: str, expense_id: str):
    try:
        res = requests.delete(
            f"{SUPABASE_URL}/rest/v1/expenses",
            headers=_headers(access_token),
            params={"id": f"eq.{expense_id}"}
        )
        res.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Failed to delete expense: {e}")
        return False