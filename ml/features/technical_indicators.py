"""
Technical indicators for ML features
"""

import numpy as np
import pandas as pd


class TechnicalIndicators:
    """Calculate technical indicators"""
    
    @staticmethod
    def sma(prices: pd.Series, window: int) -> pd.Series:
        """Simple Moving Average"""
        return prices.rolling(window=window).mean()
    
    @staticmethod
    def ema(prices: pd.Series, window: int) -> pd.Series:
        """Exponential Moving Average"""
        return prices.ewm(span=window, adjust=False).mean()
    
    @staticmethod
    def rsi(prices: pd.Series, window: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def macd(
        prices: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
    ) -> pd.DataFrame:
        """MACD indicator"""
        ema_fast = TechnicalIndicators.ema(prices, fast)
        ema_slow = TechnicalIndicators.ema(prices, slow)
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return pd.DataFrame({
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram,
        })
    
    @staticmethod
    def bollinger_bands(
        prices: pd.Series,
        window: int = 20,
        num_std: float = 2.0,
    ) -> pd.DataFrame:
        """Bollinger Bands"""
        sma = TechnicalIndicators.sma(prices, window)
        std = prices.rolling(window=window).std()
        upper = sma + (std * num_std)
        lower = sma - (std * num_std)
        
        return pd.DataFrame({
            "middle": sma,
            "upper": upper,
            "lower": lower,
            "bandwidth": (upper - lower) / sma,
        })
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
        """Average True Range"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=window).mean()
    
    @staticmethod
    def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """On-Balance Volume"""
        obv = (np.sign(close.diff()) * volume).cumsum()
        return obv
    
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        result = df.copy()
        
        # Moving averages
        result["sma_20"] = TechnicalIndicators.sma(df["close"], 20)
        result["sma_50"] = TechnicalIndicators.sma(df["close"], 50)
        result["ema_12"] = TechnicalIndicators.ema(df["close"], 12)
        result["ema_26"] = TechnicalIndicators.ema(df["close"], 26)
        
        # Momentum
        result["rsi"] = TechnicalIndicators.rsi(df["close"])
        
        # MACD
        macd_df = TechnicalIndicators.macd(df["close"])
        result = pd.concat([result, macd_df], axis=1)
        
        # Bollinger Bands
        bb_df = TechnicalIndicators.bollinger_bands(df["close"])
        result = pd.concat([result, bb_df.add_prefix("bb_")], axis=1)
        
        # Volatility
        result["atr"] = TechnicalIndicators.atr(df["high"], df["low"], df["close"])
        
        # Volume
        result["obv"] = TechnicalIndicators.obv(df["close"], df["volume"])
        
        return result
