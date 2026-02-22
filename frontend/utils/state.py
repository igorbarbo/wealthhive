"""
Session state management
"""

import streamlit as st


def init_session_state():
    """Initialize session state variables"""
    defaults = {
        "user": None,
        "portfolio": None,
        "alerts": [],
        "watchlist": [],
        "theme": "light",
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_state(key):
    """Get state value"""
    return st.session_state.get(key)


def set_state(key, value):
    """Set state value"""
    st.session_state[key] = value


def clear_state(key):
    """Clear state value"""
    if key in st.session_state:
        del st.session_state[key]
      
