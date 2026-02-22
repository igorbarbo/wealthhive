"""
Technical analysis page
"""

import streamlit as st


def show():
    """Show analysis page"""
    st.header("Análise Técnica")
    
    symbol = st.text_input("Ativo", "PETR4")
    
    if st.button("Analisar"):
        # Fetch data
        st.subheader(f"Análise de {symbol}")
        
        # Price chart with indicators
        st.write("Gráfico de Preço")
        
        # Indicators
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("RSI (14)", "65.4", "Sobrecomprado")
        
        with col2:
            st.metric("MACD", "Bullish", "Sinal de Compra")
        
        with col3:
            st.metric("Média 20", "R$ 28.50", "Acima")
        
        # ML Prediction
        st.subheader("Previsão ML")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Previsão 5 dias", "R$ 31.20", "+4.0%")
        
        with col2:
            st.metric("Confiança", "75%", "Alta")
          
