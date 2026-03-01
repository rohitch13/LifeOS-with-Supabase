import streamlit as st
from streamlit_supabase_auth import login_form, logout_button

from config import SUPABASE_URL, SUPABASE_KEY
from styles import apply_styles
from views import expenses as expenses_view

st.set_page_config(page_title="LifeOS", page_icon="💰", layout="wide", initial_sidebar_state="collapsed")

apply_styles()

st.markdown("""
<style>
    [data-testid="collapsedControl"] { display: none; }
    section[data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="display:flex;flex-direction:column;align-items:center;padding:40px 20px 10px;">
    <div class="logo-text">LifeOS</div>
    <p style="color:#6b6b80;font-size:1.1rem;font-weight:300;">Your personal finance & life tracker</p>
</div>
""", unsafe_allow_html=True)

session = login_form(url=SUPABASE_URL, apiKey=SUPABASE_KEY, providers=["google"])

if not session:
    st.stop()

# Pass access token directly — fresh every reload
access_token = session.get("access_token", "")
user_id = session["user"]["id"]
email = session["user"]["email"]
name = session["user"].get("user_metadata", {}).get("full_name", email)

# Header
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown('<div class="logo-text" style="font-size:2rem">LifeOS 💰</div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="user-pill" style="text-align:right; margin-top:6px">👤 {name}</div>', unsafe_allow_html=True)
    logout_button()

st.divider()

expenses_view.show(access_token, user_id)