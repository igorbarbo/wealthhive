"""
Main Streamlit application
"""

import streamlit as st

st.set_page_config(
    page_title="WealthHive",
    page_icon="🐝",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    """Main app entry point"""
    st.title("🐝 WealthHive")
    st.subheader("Plataforma Quantitativa de Investimentos")
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navegação",
        [
            "Dashboard",
            "Portfólio",
            "Análise Técnica",
            "Backtesting",
            "Sentimento",
            "Configurações",
        ],
    )
    
    if page == "Dashboard":
        from frontend.pages import dashboard
        dashboard.show()
    
    elif page == "Portfólio":
        from frontend.pages import portfolio
        portfolio.show()
    
    elif page == "Análise Técnica":
        from frontend.pages import analysis
        analysis.show()
    
    elif page == "Backtesting":
        from frontend.pages import backtest
        backtest.show()
    
    elif page == "Sentimento":
        from frontend.pages import sentiment
        sentiment.show()
    
    elif page == "Configurações":
        from frontend.pages import settings
        settings.show()


if __name__ == "__main__":
    main()
  
