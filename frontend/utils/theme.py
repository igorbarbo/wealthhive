"""
Theme customization
"""

import streamlit as st


def apply_theme():
    """Apply custom theme"""
    # Custom CSS
    st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        background-color: #ff6b6b;
        color: white;
    }
    .stMetric {
        background-color: white;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)


def toggle_theme():
    """Toggle between light and dark theme"""
    current = st.session_state.get("theme", "light")
    new_theme = "dark" if current == "light" else "light"
    st.session_state["theme"] = new_theme
    return new_theme


def get_theme_colors():
    """Get current theme colors"""
    theme = st.session_state.get("theme", "light")
    
    if theme == "dark":
        return {
            "background": "#1a1a1a",
            "text": "#ffffff",
            "primary": "#ff6b6b",
        }
    else:
        return {
            "background": "#ffffff",
            "text": "#000000",
            "primary": "#ff6b6b",
        }
      
