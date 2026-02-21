"""
Generate backtest reports
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd


class ReportGenerator:
    """Generate backtest reports"""
    
    def __init__(self, results: Dict[str, Any]):
        self.results = results
    
    def generate_html(self) -> str:
        """Generate HTML report"""
        html = f"""
        <html>
        <head><title>Backtest Report</title></head>
        <body>
            <h1>Backtest Results</h1>
            <h2>Performance Summary</h2>
            <table>
                <tr><td>Total Return</td><td>{self.results.get('total_return', 0):.2%}</td></tr>
                <tr><td>Sharpe Ratio</td><td>{self.results.get('sharpe_ratio', 0):.2f}</td></tr>
                <tr><td>Max Drawdown</td><td>{self.results.get('max_drawdown', 0):.2%}</td></tr>
                <tr><td>Total Trades</td><td>{self.results.get('total_trades', 0)}</td></tr>
                <tr><td>Win Rate</td><td>{self.results.get('win_rate', 0):.2%}</td></tr>
            </table>
        </body>
        </html>
        """
        return html
    
    def generate_charts(self, output_dir: str):
        """Generate performance charts"""
        # Equity curve
        equity = pd.Series(self.results.get("equity_curve", []))
        
        plt.figure(figsize=(12, 6))
        plt.plot(equity)
        plt.title("Equity Curve")
        plt.xlabel("Trade")
        plt.ylabel("Portfolio Value")
        plt.savefig(f"{output_dir}/equity_curve.png")
        plt.close()
        
        # Drawdown
        peak = equity.expanding().max()
        drawdown = (equity - peak) / peak
        
        plt.figure(figsize=(12, 6))
        plt.fill_between(range(len(drawdown)), drawdown, 0, color="red", alpha=0.3)
        plt.title("Drawdown")
        plt.xlabel("Trade")
        plt.ylabel("Drawdown %")
        plt.savefig(f"{output_dir}/drawdown.png")
        plt.close()
    
    def save_pdf(self, output_path: str):
        """Save report as PDF"""
        # Would use reportlab or weasyprint
        pass
