"""
Portfolio management page
"""

import streamlit as st


def show():
    """Show portfolio page"""
    st.header("Gerenciamento de Portfólio")
    
    # Portfolio selector
    portfolio = st.selectbox(
        "Selecionar Portfólio",
        ["Principal", "Aposentadoria", "Especulativo"],
    )
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Posições", "Performance", "Rebalanceamento"])
    
    with tab1:
        st.subheader("Posições Atuais")
        
        # Position table
        positions = {
            "Ativo": ["PETR4", "VALE3", "ITUB4", "BBDC4"],
            "Quantidade": [100, 50, 200, 300],
            "Preço Médio": [R$ 28.50, R$ 68.20, R$ 32.10, R$ 18.90],
            "Preço Atual": [R$ 30.00, R$ 70.00, R$ 33.00, R$ 19.50],
            "P&L": [R$ 150.00, R$ 90.00, R$ 180.00, R$ 180.00],
        }
        
        st.dataframe(positions)
        
        # Add position
        st.subheader("Adicionar Posição")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ativo = st.text_input("Ativo")
        
        with col2:
            quantidade = st.number_input("Quantidade", min_value=0)
        
        with col3:
            preco = st.number_input("Preço", min_value=0.0)
        
        if st.button("Adicionar"):
            st.success(f"Adicionado {quantidade} {ativo} a R$ {preco}")
    
    with tab2:
        st.subheader("Performance Histórica")
        # Show performance charts
    
    with tab3:
        st.subheader("Rebalanceamento")
        # Show rebalance recommendations
      
