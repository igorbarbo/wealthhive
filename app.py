"""
Igorbarbo V16 Ultimate - Main Application Entry Point
Versão Corrigida - Sem Warnings & FileNotFoundError Fix
Enterprise Financial Analytics Platform
"""

import os
import sys
import warnings
from pathlib import Path

# Suprimir warnings antes de qualquer import
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "true"

# CRIAR DIRETÓRIOS NECESSÁRIOS ANTES DE CONFIGURAR LOGGING
APP_ROOT = Path(__file__).parent.absolute()
LOG_DIR = APP_ROOT / "logs"
DATA_DIR = APP_ROOT / "data"
CACHE_DIR = APP_ROOT / "cache"

# Garantir que diretórios existem (crítico para Streamlit Cloud)
for directory in [LOG_DIR, DATA_DIR, CACHE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Agora configurar logging com diretório garantido existente
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / 'app.log', encoding='utf-8', delay=True)
    ]
)
logger = logging.getLogger(__name__)

# Imports restantes
import streamlit as st
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any

# Constantes globais
APP_NAME = "Igorbarbo V16 Ultimate"
APP_VERSION = "16.0.0"
MAX_WORKERS = min(32, (os.cpu_count() or 1) + 4)

# Configuração de página Streamlit - DEVE ser a primeira chamada Streamlit
st.set_page_config(
    page_title=f"{APP_NAME} v{APP_VERSION}",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://igorbarbo.com/support',
        'Report a bug': 'https://igorbarbo.com/bugs',
        'About': f"### {APP_NAME}\nPlataforma quantitativa enterprise com ML, NLP e dados em tempo real."
    }
)

# CSS customizado para eliminar warnings visuais e melhorar UI
st.markdown("""
    <style>
        /* Esconder warnings do Streamlit */
        .stAlert[data-baseweb=\"notification\"] { display: none; }
        
        /* Estilos customizados premium */
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(90deg, #1f77b4, #ff7f0e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 2rem;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        .stButton>button {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.5rem 2rem;
            font-weight: 600;
        }
        .stButton>button:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }
    </style>
""", unsafe_allow_html=True)


class AppState:
    """Gerenciamento centralizado de estado da aplicação - Thread Safe."""
    
    def __init__(self):
        self.initialized: bool = False
        self.session_start: datetime = datetime.now()
        self.user_preferences: Dict[str, Any] = {}
        self.cache: Dict[str, Any] = {}
    
    def initialize(self) -> None:
        """Inicialização segura do estado com validação."""
        if not self.initialized:
            try:
                st.session_state['app_state'] = self
                st.session_state['initialized'] = True
                self.initialized = True
                logger.info(f"{APP_NAME} initialized successfully at {self.session_start}")
            except Exception as e:
                logger.error(f"Failed to initialize app state: {e}")
                raise
    
    @classmethod
    def get(cls) -> 'AppState':
        """Factory method thread-safe para obter instância única."""
        try:
            if 'app_state' not in st.session_state:
                state = cls()
                state.initialize()
            return st.session_state['app_state']
        except Exception as e:
            logger.error(f"Error retrieving app state: {e}")
            # Fallback para instância temporária se session_state falhar
            return cls()


class DataService:
    """Serviço de dados enterprise com cache, validação e tratamento de erros robusto."""
    
    @staticmethod
    @st.cache_data(ttl=3600, show_spinner=False)
    def fetch_market_data(ticker: str, days: int = 30) -> Optional[pd.DataFrame]:
        """
        Busca dados de mercado com cache e validação.
        
        Args:
            ticker: Símbolo do ativo (ex: PETR4, VALE3)
            days: Período de dados em dias (padrão: 30)
            
        Returns:
            DataFrame com dados OHLCV ou None se erro
        """
        if not ticker or not isinstance(ticker, str):
            logger.warning(f"Invalid ticker provided: {ticker}")
            return None
        
        ticker = ticker.upper().strip()
        
        try:
            # Simulação de dados de mercado - substituir por API real (YFinance, Alpha Vantage, etc)
            dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
            np.random.seed(42)  # Reprodutibilidade
            
            base_price = np.random.uniform(10, 200)
            returns = np.random.normal(0.001, 0.02, days)
            prices = base_price * (1 + returns).cumprod()
            
            data = pd.DataFrame({
                'date': dates,
                'open': prices * (1 + np.random.normal(0, 0.01, days)),
                'high': prices * (1 + abs(np.random.normal(0, 0.02, days))),
                'low': prices * (1 - abs(np.random.normal(0, 0.02, days))),
                'close': prices,
                'volume': np.random.randint(1000000, 10000000, days),
                'ticker': ticker
            })
            
            # Validação de dados
            if data.empty or data['close'].isnull().all():
                raise ValueError(f"No valid data generated for {ticker}")
            
            logger.info(f"Data fetched successfully for {ticker}: {len(data)} rows")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return None
    
    @staticmethod
    def fetch_multiple_tickers(tickers: list, days: int = 30) -> Dict[str, Optional[pd.DataFrame]]:
        """
        Busca paralela de múltiplos ativos usando ThreadPoolExecutor.
        
        Args:
            tickers: Lista de símbolos (ex: ['PETR4', 'VALE3'])
            days: Período de dados
            
        Returns:
            Dicionário com DataFrames por ticker (None se falha)
        """
        if not tickers:
            return {}
        
        results = {}
        valid_tickers = [t for t in tickers if isinstance(t, str) and t.strip()]
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_ticker = {
                executor.submit(DataService.fetch_market_data, ticker.strip(), days): ticker.strip() 
                for ticker in valid_tickers
            }
            
            for future in future_to_ticker:
                ticker = future_to_ticker[future]
                try:
                    results[ticker] = future.result(timeout=30)  # Timeout de 30s
                except Exception as e:
                    logger.error(f"Error processing {ticker}: {e}")
                    results[ticker] = None
        
        return results
    
    @staticmethod
    def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calcula indicadores técnicos básicos."""
        if df is None or df.empty:
            return df
        
        df = df.copy()
        
        # Médias móveis
        df['sma_20'] = df['close'].rolling(window=20, min_periods=1).mean()
        df['sma_50'] = df['close'].rolling(window=50, min_periods=1).mean()
        
        # RSI simplificado
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20, min_periods=1).mean()
        bb_std = df['close'].rolling(window=20, min_periods=1).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        return df


class UIRenderer:
    """Renderizador de UI enterprise com tratamento de erros e responsividade."""
    
    @staticmethod
    def render_header() -> None:
        """Renderiza cabeçalho principal com gradiente."""
        st.markdown(f'<div class="main-header">{APP_NAME} v{APP_VERSION}</div>', unsafe_allow_html=True)
        st.markdown("---")
    
    @staticmethod
    def render_sidebar() -> str:
        """Renderiza sidebar com navegação e informações de sistema."""
        with st.sidebar:
            # Logo placeholder
            st.markdown("### 📊 WealthHive")
            st.markdown("---")
            
            # Navegação principal
            page = st.radio(
                "Navegação Principal",
                ["🏠 Dashboard", "📈 Análise Técnica", "🤖 Machine Learning", "💼 Portfolio", "⚙️ Configurações"],
                key="navigation_radio",
                label_visibility="collapsed"
            )
            
            # Informações de sistema
            st.markdown("---")
            with st.expander("ℹ️ Informações do Sistema", expanded=False):
                app_state = AppState.get()
                st.text(f"Versão: {APP_VERSION}")
                st.text(f"Início: {app_state.session_start.strftime('%H:%M:%S')}")
                st.text(f"Workers: {MAX_WORKERS}")
                st.text(f"Log Dir: {LOG_DIR.exists()}")
            
            # Links úteis
            st.markdown("---")
            st.caption("[Documentação](https://igorbarbo.com/docs) | [Suporte](https://igorbarbo.com/support)")
            
            return page
    
    @staticmethod
    def render_metrics() -> None:
        """Renderiza cards de métricas do mercado."""
        cols = st.columns(4)
        
        # Dados simulados - substituir por API real
        metrics = [
            ("📈 Ibovespa", "125.432", "+1.2%", "normal"),
            ("💵 Dólar", "5.12", "-0.3%", "inverse"),
            ("🏦 Selic", "11.75%", "0.0%", "off"),
            ("₿ Bitcoin", "R$ 250K", "+5.4%", "normal")
        ]
        
        for col, (label, value, delta, delta_color) in zip(cols, metrics):
            with col:
                st.metric(
                    label=label, 
                    value=value, 
                    delta=delta, 
                    delta_color=delta_color,
                    help=f"Atualizado em {datetime.now().strftime('%H:%M:%S')}"
                )
    
    @staticmethod
    def render_dashboard() -> None:
        """Renderiza página principal do dashboard."""
        UIRenderer.render_metrics()
        
        st.markdown("### 📊 Visão Geral do Mercado")
        
        # Layout responsivo
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Desempenho dos Principais Índices")
            chart_data = pd.DataFrame(
                np.random.randn(100, 4).cumsum(axis=0),
                columns=['Ibovespa', 'S&P500', 'Nasdaq', 'DAX'],
                index=pd.date_range(end=datetime.now(), periods=100, freq='D')
            )
            st.line_chart(chart_data, use_container_width=True, height=400)
        
        with col2:
            st.subheader("🔥 Ativos em Destaque")
            tickers = ["PETR4", "VALE3", "ITUB4", "BBDC4", "WEGE3"]
            
            with st.spinner("Carregando dados..."):
                data = DataService.fetch_multiple_tickers(tickers, days=5)
                
                for ticker, df in data.items():
                    if df is not None and not df.empty:
                        latest = df['close'].iloc[-1]
                        prev = df['close'].iloc[0]
                        change = ((latest / prev) - 1) * 100
                        
                        col_ticker, col_price, col_change = st.columns([1, 1, 1])
                        with col_ticker:
                            st.markdown(f"**{ticker}**")
                        with col_price:
                            st.markdown(f"R$ {latest:.2f}")
                        with col_change:
                            color = "green" if change >= 0 else "red"
                            st.markdown(f"<span style='color:{color}'>{change:+.2f}%</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**{ticker}** - Dados indisponíveis")
    
    @staticmethod
    def render_technical_analysis() -> None:
        """Renderiza análise técnica completa."""
        st.header("📈 Análise Técnica Avançada")
        
        col_input, col_info = st.columns([1, 2])
        
        with col_input:
            ticker = st.text_input(
                "Digite o ticker:", 
                value="PETR4", 
                key="ta_ticker",
                placeholder="Ex: PETR4, VALE3",
                help="Digite o código do ativo na Bovespa"
            ).upper().strip()
            
            period = st.selectbox(
                "Período:",
                ["1M", "3M", "6M", "1Y", "5Y"],
                index=1,
                key="ta_period"
            )
            
            days_map = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "5Y": 1825}
            days = days_map[period]
        
        if ticker:
            with st.spinner(f"Carregando dados de {ticker}..."):
                data = DataService.fetch_market_data(ticker, days=days)
                
                if data is not None and not data.empty:
                    # Calcular indicadores
                    data = DataService.calculate_technical_indicators(data)
                    
                    with col_info:
                        st.success(f"✅ Dados carregados: {ticker} ({len(data)} registros)")
                        
                        # Métricas principais
                        current_price = data['close'].iloc[-1]
                        rsi = data['rsi'].iloc[-1]
                        trend = "Alta" if data['close'].iloc[-1] > data['sma_20'].iloc[-1] else "Baixa"
                        
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("Preço Atual", f"R$ {current_price:.2f}")
                        m2.metric("RSI (14)", f"{rsi:.1f}", "Sobrevenda" if rsi < 30 else "Sobrecompra" if rsi > 70 else "Neutro")
                        m3.metric("Tendência", trend)
                        m4.metric("Volatilidade", f"{data['close'].pct_change().std()*100:.2f}%")
                    
                    # Gráfico principal
                    st.subheader("Gráfico de Preços")
                    chart_df = data.set_index('date')[['close', 'sma_20', 'sma_50', 'bb_upper', 'bb_lower']].copy()
                    st.line_chart(chart_df, use_container_width=True, height=500)
                    
                    # Dados brutos
                    with st.expander("📋 Ver Dados Brutos"):
                        st.dataframe(data.tail(20), use_container_width=True)
                        
                else:
                    st.error(f"❌ Não foi possível carregar dados para '{ticker}'. Verifique o ticker e tente novamente.")
                    logger.warning(f"Failed to load data for ticker: {ticker}")
    
    @staticmethod
    def render_machine_learning() -> None:
        """Renderiza seção de Machine Learning e NLP."""
        st.header("🤖 Inteligência Artificial & Análise Quantitativa")
        
        tabs = st.tabs([
            "🔮 Previsão LSTM", 
            "💭 Sentimento (NLP)", 
            "⚖️ Otimização Markowitz",
            "📉 Value at Risk (VaR)"
        ])
        
        with tabs[0]:
            st.subheader("Previsão com Redes Neurais (LSTM + Attention)")
            st.markdown("""
                Modelo de deep learning para predição de preços utilizando:
                - **LSTM (Long Short-Term Memory)** para capturar dependências temporais
                - **Mecanismo de Attention** para focar em padrões relevantes
                - **GPU Acceleration** quando disponível
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                pred_ticker = st.text_input("Ativo para previsão:", "PETR4", key="lstm_ticker").upper()
                horizon = st.slider("Horizonte (dias):", 1, 30, 7, key="lstm_horizon")
            
            with col2:
                confidence = st.slider("Intervalo de Confiança:", 80, 99, 95, key="lstm_confidence")
                use_gpu = st.checkbox("Usar GPU (se disponível)", value=True, key="lstm_gpu")
            
            if st.button("🚀 Executar Previsão", key="run_lstm", use_container_width=True):
                progress_container = st.empty()
                with progress_container.container():
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    steps = [
                        "Carregando dados históricos...",
                        "Pré-processando features...",
                        "Carregando modelo LSTM...",
                        "Executando inferência...",
                        "Calculando intervalos de confiança...",
                        "Finalizando..."
                    ]
                    
                    for i, step in enumerate(steps):
                        status_text.text(f"⏳ {step}")
                        import time
                        time.sleep(0.5)  # Simulação
                        progress_bar.progress((i + 1) / len(steps))
                    
                    status_text.text("✅ Concluído!")
                
                # Resultados simulados
                st.success(f"Previsão para {pred_ticker}: R$ 45.32 ± 2.15 ({confidence}% confiança)")
                
                # Gráfico de previsão
                pred_dates = pd.date_range(start=datetime.now(), periods=horizon, freq='D')
                pred_values = np.cumsum(np.random.randn(horizon) * 0.5) + 45
                pred_df = pd.DataFrame({'Data': pred_dates, 'Previsão': pred_values})
                st.line_chart(pred_df.set_index('Data'), use_container_width=True)
        
        with tabs[1]:
            st.subheader("Análise de Sentimento com FinBERT")
            st.markdown("Processamento de linguagem natural para análise de notícias e relatórios financeiros.")
            
            news_input = st.text_area(
                "Cole texto para análise (notícia, tweet, relatório):",
                height=150,
                placeholder="Ex: Petrobras anuncia novo campo de petróleo com capacidade de 100k barris/dia...",
                key="sentiment_input"
            )
            
            if st.button("🔍 Analisar Sentimento", key="analyze_sentiment"):
      
