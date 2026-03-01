import streamlit as st

def apply_styles():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono&display=swap');
        * { font-family: 'DM Sans', sans-serif; }
        .stApp { background: #f5f5fa; color: #1a1a2e; }
        .logo-text {
            font-size: 3.5rem; font-weight: 700;
            background: linear-gradient(135deg, #7c6af7, #a78bfa, #60a5fa);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            letter-spacing: -2px; margin-bottom: 8px;
        }
        .stButton > button {
            background: linear-gradient(135deg, #7c6af7, #60a5fa) !important;
            color: white !important; border: none !important;
            border-radius: 10px !important; font-weight: 600 !important;
            padding: 10px 24px !important;
        }
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div,
        .stDateInput > div > div > input {
            background: #ffffff !important; border: 1px solid #e0e0ee !important;
            color: #1a1a2e !important; border-radius: 10px !important;
        }
        div[data-testid="stForm"] {
            background: #ffffff; border: 1px solid #e0e0ee;
            border-radius: 16px; padding: 24px;
        }
        div[data-testid="stMetric"] {
            background: #ffffff; border: 1px solid #e0e0ee;
            border-radius: 12px; padding: 16px;
        }
        .user-pill {
            background: #ffffff; border: 1px solid #e0e0ee;
            border-radius: 20px; padding: 6px 14px; font-size: 0.85rem; color: #6060a0;
        }
        .tag-badge {
            display: inline-block; background: #ede9ff; border-radius: 6px;
            padding: 2px 8px; font-size: 0.75rem; color: #6d4af7;
            margin-right: 4px; font-family: 'DM Mono', monospace;
        }
        .recurring-badge {
            display: inline-block; background: #efffef; border: 1px solid #a0e0a0;
            border-radius: 6px; padding: 2px 8px; font-size: 0.75rem; color: #1a8a1a;
            margin-right: 4px;
        }
        hr { border-color: #e0e0ee !important; }
        p, label, .stMarkdown { color: #1a1a2e !important; }
        small { color: #9090a8 !important; }
    </style>
    """, unsafe_allow_html=True)