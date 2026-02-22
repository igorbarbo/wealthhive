"""
Card components
"""

import streamlit as st


def metric_card(title, value, delta=None, delta_color="normal"):
    """Create metric card"""
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color,
    )


def info_card(title, content, icon="ℹ️"):
    """Create info card"""
    with st.container():
        st.subheader(f"{icon} {title}")
        st.write(content)


def success_card(message):
    """Create success card"""
    st.success(message)


def warning_card(message):
    """Create warning card"""
    st.warning(message)


def error_card(message):
    """Create error card"""
    st.error(message)
  
