"""
Form components
"""

import streamlit as st


def order_form():
    """Trading order form"""
    with st.form("order_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            symbol = st.text_input("Ativo")
            order_type = st.selectbox(
                "Tipo",
                ["Mercado", "Limite", "Stop"],
            )
        
        with col2:
            quantity = st.number_input("Quantidade", min_value=1)
            price = st.number_input("Preço", min_value=0.0)
        
        side = st.radio("Lado", ["Compra", "Venda"], horizontal=True)
        
        submitted = st.form_submit_button("Enviar Ordem")
        
        if submitted:
            return {
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "order_type": order_type,
                "price": price,
            }
    
    return None


def alert_form():
    """Price alert form"""
    with st.form("alert_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            symbol = st.text_input("Ativo")
            condition = st.selectbox(
                "Condição",
                ["Acima de", "Abaixo de"],
            )
        
        with col2:
            target_price = st.number_input("Preço Alvo", min_value=0.0)
            notification = st.selectbox(
                "Notificação",
                ["Email", "Push", "Ambos"],
            )
        
        submitted = st.form_submit_button("Criar Alerta")
        
        if submitted:
            return {
                "symbol": symbol,
                "condition": condition,
                "target_price": target_price,
                "notification": notification,
            }
    
    return None
  
