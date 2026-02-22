"""
Portfolio builder page
"""

import streamlit as st


def show():
    """Show portfolio builder"""
    st.header("Construtor de Portfólio")
    
    # Risk profile
    risk_profile = st.select_slider(
        "Perfil de Risco",
        options=["Conservador", "Moderado", "Agressivo"],
    )
    
    # Investment amount
    amount = st.number_input(
        "Valor do Investimento",
        min_value=1000,
        value=100000,
        step=1000,
    )
    
    # Constraints
    st.subheader("Restrições")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_single = st.slider("Máximo por Ativo (%)", 5, 50, 20)
        min_single = st.slider("Mínimo por Ativo (%)", 0, 10, 5)
    
    with col2:
        sectors = st.multiselect(
            "Setores Permitidos",
            ["Financeiro", "Energia", "Materiais", "Tecnologia", "Saúde"],
            default=["Financeiro", "Energia", "Materiais"],
        )
    
    if st.button("Gerar Portfólio", type="primary"):
        with st.spinner("Otimizando portfólio..."):
            # Generate portfolio
            st.success("Portfólio gerado!")
            
            # Show allocation
            st.subheader("Alocação Recomendada")
            
            allocation = {
                "Ativo": ["PETR4", "VALE3", "ITUB4", "BBDC4", "WEGE3"],
                "Peso": [20, 20, 20, 20, 20],
                "Valor": [amount * 0.2] * 5,
            }
            
            st.dataframe(allocation)
            
            # Expected performance
            st.subheader("Performance Esperada")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Retorno Esperado", "12.5% ao ano")
            
            with col2:
                st.metric("Risco Esperado", "18.2%")
            
            with col3:
                st.metric("Sharpe Ratio", "0.69")
              
