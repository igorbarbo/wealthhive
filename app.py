"""
WealthHive - Sistema de Gestão de Investimentos com IA
Streamlit App - Versão Enterprise
"""

from typing import Any, Dict

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta


class WealthHiveApp:
    """
    Main application class
    """
    
    def __init__(self):
        """Initialize app state"""
        self.setup_page()
        self.init_session_state()
    
    def setup_page(self):
        """Configure Streamlit page"""
        st.set_page_config(
            page_title="WealthHive - Gestão Inteligente",
            page_icon="🐝",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
        # Dark theme CSS
        st.markdown("""
        <style>
            .main { background-color: #0d1117; color: #ffffff; }
            .stApp { background-color: #0d1117; }
            .metric-card { 
                background-color: #161b22; 
                border-radius: 12px; 
                padding: 20px; 
                border: 1px solid #30363d; 
            }
            .stButton>button { 
                background-color: #d4af37; 
                color: #000000; 
                border-radius: 8px; 
                font-weight: bold; 
            }
            h1, h2, h3 { color: #ffffff !important; }
        </style>
        """, unsafe_allow_html=True)
    
    def init_session_state(self):
        """Initialize session state variables"""
        if 'portfolio' not in st.session_state:
            st.session_state.portfolio = {
                'total_value': 257430.0,
                'change': 2.75,
                'assets': [
                    {'ticker': 'AAPL', 'name': 'Apple Inc.', 
                     'value': 39155, 'change': 1.2, 'allocation': 15},
                    {'ticker': 'TSLA', 'name': 'Tesla Inc.', 
                     'value': 51029, 'change': -0.8, 'allocation': 20},
                    {'ticker': 'BTC', 'name': 'Bitcoin', 
                     'value': 84240, 'change': 3.5, 'allocation': 33},
                    {'ticker': 'BOVA11', 'name': 'Ibovespa ETF', 
                     'value': 82341, 'change': 0.5, 'allocation': 32},
                ]
            }
    
    def format_currency(self, value: float) -> str:
        """Format value as currency"""
        return f"${value:,.2f}"
    
    def get_change_color(self, change: float) -> str:
        """Get color based on change value"""
        return "#2ecc71" if change >= 0 else "#e74c3c"
    
    def render_header(self):
        """Render app header"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.markdown(
                "<h1 style='color: #d4af37; margin: 0;'>🐝 WealthHive</h1>", 
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                "<p style='color: #8b949e; margin-top: 10px;'>"
                "Gestão Inteligente de Investimentos</p>", 
                unsafe_allow_html=True
            )
        with col3:
            st.markdown(
                "<p style='text-align: right; color: #1abc9c;'>● Online</p>", 
                unsafe_allow_html=True
            )
        
        st.divider()
    
    def generate_prediction_data(self):
        """Generate LSTM prediction data"""
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        base_price = 53200
        trend = np.linspace(0, 2000, 30)
        noise = np.random.normal(0, 300, 30)
        actual = base_price + trend + noise
        predicted = actual + np.random.normal(500, 200, 30)
        return dates, actual, predicted
    
    def render_dashboard_tab(self):
        """Render AI Dashboard tab"""
        st.markdown("## AI & Quant Prediction")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            dates, actual, predicted = self.generate_prediction_data()
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates[20:], y=predicted[20:],
                mode='lines',
                name='LSTM Prediction',
                line=dict(color='#d4af37', width=3),
                fill='tonexty',
                fillcolor='rgba(212, 175, 55, 0.1)'
            ))
            
            fig.add_trace(go.Scatter(
                x=dates[:21], y=actual[:21],
                mode='lines',
                name='Actual',
                line=dict(color='#3498db', width=3)
            ))
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='#161b22',
                font_color='#ffffff',
                height=400,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Algo Details")
            
            algos = [
                ("🧠", "LSTM + Attention", "8.0%"),
                ("📊", "FinBERT Sentiment", "70%"),
                ("🔄", "Walk-Forward Backtest", "8.9%"),
            ]
            
            for icon, name, value in algos:
                st.markdown(
                    f"**{icon} {name}**  \\n"
                    f"<span style='color:#d4af37'>{value}</span>",
                    unsafe_allow_html=True
                )
            
            st.markdown("### Model Accuracy")
            st.markdown(
                "<h1 style='color: #2ecc71;'>82%</h1>",
                unsafe_allow_html=True
            )
        
        # Quick metrics
        cols = st.columns(4)
        metrics = [
            ("Portfolio Value", "$257,430", "+2.75%"),
            ("Daily Return", "$6,890", "+1.32%"),
            ("AI Predictions", "1,240", "98.5%"),
            ("Active Alerts", "3", "1 critical")
        ]
        
        for col, (label, value, delta) in zip(cols, metrics):
            with col:
                st.metric(label=label, value=value, delta=delta)
    
    def render_portfolio_tab(self):
        """Render Portfolio tab"""
        st.markdown("## Balanced Portfolio")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            for asset in st.session_state.portfolio['assets']:
                change_color = self.get_change_color(asset['change'])
                change_icon = "▲" if asset['change'] >= 0 else "▼"
                
                cols = st.columns([2, 1, 1])
                with cols[0]:
                    st.markdown(
                        f"**{asset['ticker']}**  \\n"
                        f"<small>{asset['name']}</small>",
                        unsafe_allow_html=True
                    )
                with cols[1]:
                    st.markdown(f"**{self.format_currency(asset['value'])}**")
                with cols[2]:
                    st.markdown(
                        f"<span style='color:{change_color}'>"
                        f"{change_icon} {asset['change']}%</span>",
                        unsafe_allow_html=True
                    )
                st.divider()
        
        with col2:
            # Allocation pie chart
            allocations = [a['allocation'] for a in 
                          st.session_state.portfolio['assets']]
            labels = [a['ticker'] for a in 
                     st.session_state.portfolio['assets']]
            colors = ['#3498db', '#e74c3c', '#f39c12', '#1abc9c']
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=labels, values=allocations, hole=0.6,
                marker_colors=colors,
                textinfo='label+percent',
                textfont_color='#ffffff'
            )])
            
            fig_pie.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                height=300,
                annotations=[dict(
                    text='+892%', x=0.5, y=0.5, 
                    font_size=20, showarrow=False, 
                    font_color='#d4af37'
                )]
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
            
            st.markdown("**Monte Carlo Expected Return:** +15.2%")
            st.markdown("**Risk (VaR 95%):** -$10,285")
        
        # Action buttons
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔄 Rebalancear", use_container_width=True):
                st.success("Rebalanceamento iniciado!")
        with col_btn2:
            if st.button("⚡ Simular", use_container_width=True):
                st.info("Simulação em execução...")
    
    def render_ai_analysis_tab(self):
        """Render AI Analysis tab"""
        st.markdown("## AI-Powered Market Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            dates = pd.date_range(end=datetime.now(), 
                                 periods=100, freq='H')
            prices = 62000 + np.cumsum(np.random.randn(100) * 100)
            
            fig_tech = go.Figure()
            fig_tech.add_trace(go.Scatter(
                x=dates, y=prices,
                mode='lines',
                name='Price',
                line=dict(color='#1abc9c', width=2),
                fill='tozeroy',
                fillcolor='rgba(26, 188, 156, 0.1)'
            ))
            
            fig_tech.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='#161b22',
                height=450
            )
            
            st.plotly_chart(fig_tech, use_container_width=True)
        
        with col2:
            st.markdown("### Model Performance")
            
            models = [
                ("LSTM Predictor", 0.82, "12ms"),
                ("FinBERT Sentiment", 0.89, "45ms"),
                ("Risk Classifier", 0.91, "8ms"),
            ]
            
            for name, accuracy, latency in models:
                st.markdown(
                    f"**{name}**  \\n"
                    f"Accuracy: {accuracy:.0%} | Latency: {latency}"
                )
            
            st.markdown("### Feature Importance")
            features = [
                ("Price Momentum", 0.35), 
                ("Volume", 0.25), 
                ("Sentiment", 0.20)
            ]
            for feat, imp in features:
                st.progress(imp, text=f"{feat}")
    
    def render_news_tab(self):
        """Render News & Sentiment tab"""
        st.markdown("## News Sentiment Analysis")
        
        # Main news card
        st.markdown("""
        <div style='background-color: #161b22; padding: 20px; 
                    border-radius: 12px; 
                    border-left: 4px solid #1abc9c;'>
            <h3>WEF 2024: Nvidia CEO says ChatGPT is the 
            "iPhone moment" of AI</h3>
            <p>Sentiment Score: 
            <span style='color:#2ecc71; font-size:24px; 
            font-weight:bold;'>0.744 🐂 BULLISH</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Topics
        st.markdown("### Key Topics")
        topics = ["Artificial Intelligence", "ChatGPT", 
                 "NVIDIA", "Deep Learning"]
        cols = st.columns(len(topics))
        for col, topic in zip(cols, topics):
            with col:
                st.markdown(
                    f"<div style='text-align:center; padding:10px; "
                    f"background-color:#161b22; border-radius:8px; "
                    f"border:1px solid #1abc9c; color:#1abc9c;'>"
                    f"{topic}</div>",
                    unsafe_allow_html=True
                )
        
        # Related news
        st.markdown("### Related News")
        news_items = [
            ("ChatGPT is 'iPhone moment' of AI: Nvidia CEO", 
             "2h ago", 0.85),
            ("NVIDIA reaches all-time high", "4h ago", 0.92),
            ("Tech stocks rally", "6h ago", 0.78),
        ]
        
        for title, time, score in news_items:
            color = "#2ecc71" if score > 0.5 else "#e74c3c"
            st.markdown(
                f"**{title}**  \\n"
                f"<small>{time}</small> | "
                f"<span style='color:{color}; font-weight:bold;'>"
                f"{score:.0%}</span>",
                unsafe_allow_html=True
            )
    
    def render_monitoring_tab(self):
        """Render System Monitoring tab"""
        st.markdown("## System Monitoring")
        
        # System metrics
        cols = st.columns(4)
        system_metrics = [
            ("CPU", "45%", "#2ecc71"),
            ("Memory", "62%", "#f39c12"),
            ("Disk", "78%", "#3498db"),
            ("Network", "1.2 GB/s", "#1abc9c"),
        ]
        
        for col, (label, value, color) in zip(cols, system_metrics):
            with col:
                st.markdown(
                    f"<div style='background-color: #161b22; "
                    f"padding: 15px; border-radius: 8px; "
                    f"border-left: 4px solid {color};'>"
                    f"<p style='margin:0; color:#8b949e;'>{label}</p>"
                    f"<h3 style='margin:5px 0; color:#ffffff;'>"
                    f"{value}</h3></div>",
                    unsafe_allow_html=True
                )
        
        # Charts
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### CPU Usage")
            cpu_data = np.random.randint(30, 80, 50)
            fig_cpu = go.Figure()
            fig_cpu.add_trace(go.Scatter(
                y=cpu_data, mode='lines', fill='tozeroy',
                line=dict(color='#2ecc71')
            ))
            fig_cpu.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='#161b22',
                height=200
            )
            st.plotly_chart(fig_cpu, use_container_width=True)
        
        with col2:
            st.markdown("### Memory Usage")
            mem_data = np.random.randint(50, 75, 50)
            fig_mem = go.Figure()
            fig_mem.add_trace(go.Scatter(
                y=mem_data, mode='lines', fill='tozeroy',
                line=dict(color='#f39c12')
            ))
            fig_mem.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='#161b22',
                height=200
            )
            st.plotly_chart(fig_mem, use_container_width=True)
        
        # Alerts
        st.markdown("### Active Alerts")
        alerts = [
            ("🔴 High Memory", "2 min ago", "critical"),
            ("🟡 API Latency", "5 min ago", "warning"),
            ("🟢 Backup OK", "1h ago", "info"),
        ]
        
        for icon, message, level in alerts:
            color = "#e74c3c" if level == "critical" \
                   else "#f39c12" if level == "warning" \
                   else "#2ecc71"
            st.markdown(
                f"<span style='color:{color};'>{icon}</span> "
                f"**{message}**",
                unsafe_allow_html=True
            )
    
    def render_footer(self):
        """Render app footer"""
        st.divider()
        st.markdown(
            "<div style='text-align:center; color:#8b949e;'>"
            "WealthHive v16.0 - Enterprise Quantitative Platform "
            "© 2024</div>",
            unsafe_allow_html=True
        )
    
    def run(self):
        """Main application entry point"""
        self.render_header()
        
        # Navigation tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Dashboard", "💼 Portfólio", 
            "🤖 AI Analysis", "📰 News & Sentiment", 
            "⚙️ Monitoring"
        ])
        
        with tab1:
            self.render_dashboard_tab()
        with tab2:
            self.render_portfolio_tab()
        with tab3:
            self.render_ai_analysis_tab()
        with tab4:
            self.render_news_tab()
        with tab5:
            self.render_monitoring_tab()
        
        self.render_footer()


def main():
    """Application entry point"""
    app = WealthHiveApp()
    app.run()


if __name__ == "__main__":
    main()
                      
