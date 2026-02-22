"""
Settings page
"""

import streamlit as st


def show():
    """Show settings page"""
    st.header("Configurações")
    
    # API Keys
    st.subheader("Chaves de API")
    
    with st.expander("Alpha Vantage"):
        st.text_input("API Key", type="password", key="alpha_vantage")
    
    with st.expander("B3"):
        st.text_input("API Key", type="password", key="b3")
    
    # Preferences
    st.subheader("Preferências")
    
    st.selectbox("Idioma", ["Português", "English"])
    st.selectbox("Moeda", ["BRL", "USD"])
    st.selectbox("Tema", ["Claro", "Escuro"])
    
    # Notifications
    st.subheader("Notificações")
    
    st.checkbox("Alertas de Preço")
    st.checkbox("Relatórios Diários")
    st.checkbox("Alertas de Rebalanceamento")
    
    if st.button("Salvar Configurações", type="primary"):
        st.success("Configurações salvas!")
      
