"""
Navigation components
"""

import streamlit as st


def sidebar_navigation():
    """Create sidebar navigation"""
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150.png?text=🐝", width=100)
        st.title("WealthHive")
        
        pages = {
            "Dashboard": "📊",
            "Portfólio": "💼",
            "Análise": "📈",
            "Backtest": "🧪",
            "Sentimento": "🧠",
            "Configurações": "⚙️",
        }
        
        selection = st.radio(
            "Navegação",
            list(pages.keys()),
            format_func=lambda x: f"{pages[x]} {x}",
        )
        
        st.divider()
        
        # User info
        st.write("👤 Usuário: Demo")
        st.write("💎 Plano: Premium")
        
        return selection


def breadcrumb(path):
    """Create breadcrumb navigation"""
    st.write(" > ".join(path))


def quick_actions():
    """Quick action buttons"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Nova Ordem"):
            st.session_state["show_order_form"] = True
    
    with col2:
        if st.button("🔔 Novo Alerta"):
            st.session_state["show_alert_form"] = True
    
    with col3:
        if st.button("📊 Gerar Relatório"):
            st.session_state["show_report_dialog"] = True
          
