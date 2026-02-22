"""
Rebalance dashboard page
"""

import streamlit as st


def show():
    """Show rebalance dashboard"""
    st.header("⚖️ Dashboard de Rebalanceamento")
    
    # Portfolio drift
    st.subheader("Desvio da Alocação Alvo")
    
    # Show drift chart
    drift_data = {
        "Ativo": ["PETR4", "VALE3", "ITUB4", "BBDC4", "WEGE3"],
        "Alvo": [20, 20, 20, 20, 20],
        "Atual": [25, 18, 22, 15, 20],
        "Desvio": [+5, -2, +2, -5, 0],
    }
    
    st.dataframe(drift_data)
    
    # Rebalance needed?
    max_drift = max(abs(d) for d in drift_data["Desvio"])
    
    if max_drift > 5:
        st.warning(f"⚠️ Rebalanceamento necessário! Desvio máximo: {max_drift}%")
        
        if st.button("Gerar Recomendações"):
            st.subheader("Trades Recomendados")
            
            trades = [
                {"Ação": "VENDER", "Ativo": "PETR4", "Quantidade": 10, "Valor": "R$ 300,00"},
                {"Ação": "COMPRAR", "Ativo": "BBDC4", "Quantidade": 25, "Valor": "R$ 487,50"},
            ]
            
            st.table(trades)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Turnover Estimado", "10%")
            
            with col2:
                st.metric("Custo de Transação", "R$ 15,00")
    else:
        st.success("✅ Portfólio dentro dos limites de alocação")
    
    # Auto-rebalance settings
    st.subheader("Configuração de Rebalanceamento Automático")
    
    st.checkbox("Habilitar rebalanceamento automático")
    st.selectbox("Frequência", ["Mensal", "Trimestral", "Semestral", "Anual"])
    st.slider("Limite de desvio (%)", 1, 10, 5)
  
