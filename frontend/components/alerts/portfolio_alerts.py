"""
Portfolio alert components
"""

import streamlit as st


def show_alerts(alerts):
    """Display portfolio alerts"""
    for alert in alerts:
        if alert["type"] == "price":
            st.info(f"💰 {alert['message']}")
        elif alert["type"] == "risk":
            st.warning(f"⚠️ {alert['message']}")
        elif alert["type"] == "opportunity":
            st.success(f"🎯 {alert['message']}")
        elif alert["type"] == "rebalance":
            st.warning(f"⚖️ {alert['message']}")


def alert_settings():
    """Alert configuration"""
    st.subheader("Configuração de Alertas")
    
    st.checkbox("Alertas de Preço")
    st.checkbox("Alertas de Risco (VaR)")
    st.checkbox("Alertas de Rebalanceamento")
    st.checkbox("Alertas de Oportunidade")
    st.checkbox("Relatórios Diários")
    st.checkbox("Relatórios Semanais")
  
