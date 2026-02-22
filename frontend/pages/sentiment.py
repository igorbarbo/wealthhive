"""
Sentiment analysis page
"""

import streamlit as st


def show():
    """Show sentiment page"""
    st.header("Análise de Sentimento")
    
    symbol = st.text_input("Ativo", "PETR4")
    
    if st.button("Analisar Sentimento"):
        st.subheader(f"Sentimento para {symbol}")
        
        # Overall sentiment
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Sentimento Geral", "Positivo", "+0.25")
        
        with col2:
            st.metric("Notícias Analisadas", "42", "Últimas 24h")
        
        with col3:
            st.metric("Confiança", "82%", "Alta")
        
        # Recent news
        st.subheader("Notícias Recentes")
        
        news = [
            {"title": "Petróleo sobe com tensões no Oriente Médio", "sentiment": "Positivo", "confidence": "85%"},
            {"title": "Produção da Petrobras cresce 5%", "sentiment": "Positivo", "confidence": "90%"},
            {"title": "Preocupações com dívidas do setor", "sentiment": "Negativo", "confidence": "60%"},
        ]
        
        for item in news:
            with st.expander(f"{item['title']} - {item['sentiment']}"):
                st.write(f"Confiança: {item['confidence']}")
                st.write("Análise detalhada do sentimento...")
        
        # Word cloud
        st.subheader("Nuvem de Palavras")
        # Would show word cloud
      
